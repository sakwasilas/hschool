from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify    
from connections import SessionLocal
from models import User, CompleteProfile, LiveClass, RevisionMaterial, Video
from datetime import datetime
from functools import wraps
from sqlalchemy import func

#=========================
# File Upload Config                
import os
from werkzeug.utils import secure_filename                  
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx'}
UPLOAD_FOLDER = 'static/materials'
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
#=========================


app = Flask(__name__)
app.secret_key = "silaswanyamarechosilasayangaamukowaivansamuel"

# =========================
# Role-based Access Decorator
# =========================
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if "user_id" not in session or "role" not in session:
                return redirect(url_for("login"))
            if session["role"] != required_role:
                return "Access Denied", 403
            return f(*args, **kwargs)
        return wrapped
    return decorator

# =========================
# Home Route
# =========================
@app.route('/')
def home():
    return redirect(url_for('login'))

# =========================
# Login
# =========================

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        db = SessionLocal()
        try:
            # Fetch user by username
            user = db.query(User).filter_by(username=username).first()

            if user and user.password == password:  # Plain text check
                # Set session info
                session["user_id"] = user.id
                session["role"] = user.role

                # Redirect based on role
                if user.role == "admin":
                    return redirect(url_for("admin_dashboard"))
                elif user.role == "teacher":
                    return redirect(url_for("teacher_dashboard"))
                elif user.role == "student":
                    # Check if student already has a profile
                    profile = db.query(CompleteProfile).filter_by(user_id=user.id).first()
                    if profile:
                        return redirect(url_for("student_dashboard"))
                    else:
                        return redirect(url_for("complete_profile"))
                else:
                    return "Role not recognized", 403
            else:
                flash("Invalid credentials", "danger")
        finally:
            db.close()

    return render_template("login.html")


# =========================
# Register
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        role = request.form.get("role", "student")  # default role: student

        if password != confirm_password:
            message = "Passwords do not match"
        else:
            db = SessionLocal()
            existing_user = db.query(User).filter_by(username=username).first()

            if existing_user:
                message = "Username already exists"
            else:
                # ✅ store plain password directly
                new_user = User(username=username, password=password, role=role)
                db.add(new_user)
                db.commit()
                db.close()
                return redirect(url_for('login'))

            db.close()

    return render_template('register.html', message=message)

# =========================
# Logout
# =========================
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))

# =========================
# Forgot Password
# =========================
@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        db = SessionLocal()
        user = db.query(User).filter_by(username=username).first()
        db.close()
        if user:
            return redirect(url_for('reset_password', username=username))
        else:
            message = "No account found with that username."
    return render_template('forgot_password.html', message=message)

# =========================
# Reset Password
# =========================
@app.route('/reset_password/<username>', methods=['GET', 'POST'])
def reset_password(username):
    message = ""
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        if new_password != confirm_password:
            message = "Passwords do not match."
        else:
            db = SessionLocal()
            user = db.query(User).filter_by(username=username).first()
            if user:
                user.password = generate_password_hash(new_password)
                db.commit()
                message = "Password updated successfully! You can now log in."
            db.close()
            return redirect(url_for('login'))
    return render_template('reset_password.html', message=message, username=username)

# =========================
# Complete Profile
# =========================
@app.route('/complete_profile', methods=['GET', 'POST'])
def complete_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Use context manager to auto-close session
    with SessionLocal() as db:
        # Fetch user
        user = db.query(User).filter_by(id=user_id).first()
        if not user:
            flash("User not found", "danger")
            return redirect(url_for('login'))

        # Fetch existing profile if any
        profile = db.query(CompleteProfile).filter_by(user_id=user.id).first()

        if request.method == 'POST':
            # Get form data
            first_name = request.form.get('first_name', '').strip()
            middle_name = request.form.get('middle_name', '').strip()
            last_name = request.form.get('last_name', '').strip()
            contact_no = request.form.get('contact_no', '').strip()
            guardian_name = request.form.get('guardian_name', '').strip()
            form_selected = request.form.get('form', '').strip()

            # Validate required fields
            if not first_name or not last_name or not contact_no or not guardian_name or not form_selected:
                flash("Please fill all required fields", "danger")
                profile_data = profile.__dict__ if profile else {}
                return render_template('students/complete_profile.html', profile=profile_data)

            if profile:
                # Update existing profile
                profile.first_name = first_name
                profile.middle_name = middle_name
                profile.last_name = last_name
                profile.contact_no = contact_no
                profile.guardian_name = guardian_name
                profile.form = form_selected
            else:
                # Create new profile
                profile = CompleteProfile(
                    user_id=user.id,
                    first_name=first_name,
                    middle_name=middle_name,
                    last_name=last_name,
                    contact_no=contact_no,
                    guardian_name=guardian_name,
                    form=form_selected
                )
                db.add(profile)

            db.commit()  # Save changes
            flash("Profile saved successfully!", "success")

            # Redirect to dashboard after saving
            return redirect(url_for("student_dashboard"))

        # For GET request, pass profile data to template
        profile_data = profile.__dict__ if profile else {}
        return render_template('students/complete_profile.html', profile=profile_data)


from sqlalchemy import func, or_

# =========================
# Student Dashboard
# =========================
@app.route("/student")
def student_dashboard():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    db = SessionLocal()
    try:
        # Get logged-in user
        user = db.query(User).filter_by(id=session["user_id"]).first()
        if not user:
            return redirect(url_for("login"))

        # Get student's full profile
        profile = db.query(CompleteProfile).filter_by(user_id=user.id).first()
        if not profile:
            return "Profile not found for this user", 404

        student_form = profile.form.strip().lower()  # normalize

        # ✅ Fetch Live Classes (matching form or 'all')
        live_classes = db.query(LiveClass).filter(
            func.lower(func.trim(LiveClass.form)).in_([student_form, "all", ""])
        ).all()

        # ✅ Fetch Revision Materials
        revision_materials = db.query(RevisionMaterial).filter(
            func.lower(func.trim(RevisionMaterial.form)).in_([student_form, "all", ""])
        ).all()

        # ✅ Fetch Videos
        videos = db.query(Video).filter(
            func.lower(func.trim(Video.form)).in_([student_form, "all", ""])
        ).all()

        # ✅ Pass everything to template
        return render_template(
            "students/student_dashboard.html",
            student={
                "full_name": f"{profile.first_name} {profile.last_name}",
                "form": profile.form,
                "phone": profile.contact_no,
                "guardian_name": profile.guardian_name,
            },
            live_classes=live_classes,
            revision_materials=revision_materials,
            videos=videos,
            current_year=datetime.now().year
        )

    finally:
        db.close()



# =========================
# Teacher Dashboard
# =========================
@app.route('/teacher')
@role_required("teacher")
def teacher_dashboard():
    return render_template("teacher_dashboard.html")

# =========================
# Admin Dashboard
# =========================
@app.route('/admin')
@role_required("admin")
def admin_dashboard():
    db = SessionLocal()
    live_classes = db.query(LiveClass).all()
    revision_materials = db.query(RevisionMaterial).all()
    videos = db.query(Video).all()
    current_year = datetime.now().year
    db.close()
    return render_template(
        "admin/admin_dashboard.html",
        live_classes=live_classes,
        revision_materials=revision_materials,
        videos=videos,
        current_year=current_year
    )

# =========================
# Admin CRUD - Live Classes
# =========================
@app.route("/admin/live_class/add", methods=["POST","GET"])
@role_required("admin")
def add_live_class():
    db = SessionLocal()

    title = request.form.get("title")
    link = request.form.get("link")
    time = request.form.get("time")
    form = request.form.get("form")
    subject = request.form.get("subject")  # ✅ added

    if not title or not link:
        flash("Title and Link are required!", "danger")
        db.close()
        return redirect(url_for("admin_dashboard"))

    new_class = LiveClass(
        title=title,
        link=link,
        time=time,
        form=form,
        subject=subject  # ✅ added
    )

    db.add(new_class)
    db.commit()
    db.close()
    flash("✅ Live class added successfully!", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/live_class/edit/<int:class_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_live_class(class_id):
    db = SessionLocal()
    cls = db.query(LiveClass).get(class_id)
    if request.method == "POST":
        cls.title = request.form.get("title")
        cls.link = request.form.get("link")
        cls.time = request.form.get("time")
        cls.form = request.form.get("form")
        db.commit()
        db.close()
        flash("Live class updated!", "success")
        return redirect(url_for("admin_dashboard"))
    db.close()
    return render_template("edit_live_class.html", cls=cls)

@app.route("/admin/live_class/delete/<int:class_id>", methods=["POST"])
@role_required("admin")
def delete_live_class(class_id):
    db = SessionLocal()
    cls = db.query(LiveClass).get(class_id)
    if cls:
        db.delete(cls)
        db.commit()
        flash("Live class deleted!", "success")
    else:
        flash("Class not found.", "danger")
    db.close()
    return redirect(url_for("admin_dashboard"))

@app.route('/admin/material/add', methods=['GET', 'POST'])
@role_required("admin")
def add_material():
    if request.method == 'POST':
        db = SessionLocal()
        try:
            title = request.form.get('title', '').strip()
            subject = request.form.get('subject', '').strip()
            form_class = request.form.get('form', '').strip()
            link = request.form.get('link', '').strip()
            file = request.files.get('file')

            if not title or not subject or not form_class:
                flash("All fields are required", "danger")
                return redirect(url_for('admin_dashboard'))

            # Case 1: Google Drive link
            if link:
                if "drive.google.com/file/d/" in link:
                    file_id = link.split("/d/")[1].split("/")[0]
                    link = f"https://drive.google.com/uc?export=download&id={file_id}"

            # Case 2: File upload
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                link = url_for('static', filename=f'materials/{filename}')

            else:
                flash("You must provide either a file or a Google Drive link.", "danger")
                return redirect(url_for('admin_dashboard'))

            # Save material
            new_material = RevisionMaterial(
                title=title,
                subject=subject,
                form=form_class,
                link=link
            )
            db.add(new_material)
            db.commit()
            flash("Material added successfully!", "success")

        finally:
            db.close()

    return redirect(url_for('admin_dashboard'))



@app.route("/admin/material/edit/<int:material_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_material(material_id):
    db = SessionLocal()
    mat = db.query(RevisionMaterial).get(material_id)
    if request.method == "POST":
        mat.title = request.form.get("title")
        mat.link = request.form.get("link")
        mat.form = request.form.get("form")
        db.commit()
        db.close()
        flash("Material updated!", "success")
        return redirect(url_for("admin_dashboard"))
    db.close()
    return render_template("edit_material.html", mat=mat)

@app.route("/admin/material/delete/<int:material_id>")
@role_required("admin")
def delete_material(material_id):
    db = SessionLocal()
    mat = db.query(RevisionMaterial).get(material_id)
    db.delete(mat)
    db.commit()
    db.close()
    flash("Material deleted!", "success")
    return redirect(url_for("admin_dashboard"))

# ========================= 
# Admin CRUD - Videos
# =========================

@app.route('/admin/video/add', methods=['GET', 'POST'])
@role_required("admin")
def add_video():
    if request.method == 'POST':
        db = SessionLocal()
        try:
            title = request.form.get('title', '').strip()
            link = request.form.get('link', '').strip()
            form_class = request.form.get('form', '').strip()
            subject = request.form.get('subject', '').strip()

            if not title or not link or not form_class or not subject:
                flash("All fields are required", "danger")
                return redirect(url_for('admin_dashboard'))

            # Convert Google Drive links to embeddable preview links
            if "drive.google.com/file/d/" in link:
                file_id = link.split("/d/")[1].split("/")[0]
                link = f"https://drive.google.com/file/d/{file_id}/preview"

            new_video = Video(
                title=title,
                link=link,
                form=form_class,
                subject=subject
            )
            db.add(new_video)
            db.commit()
            flash("Video added successfully!", "success")
        finally:
            db.close()

    return redirect(url_for('admin_dashboard'))


@app.route("/admin/video/edit/<int:video_id>", methods=["GET", "POST"])
@role_required("admin")
def edit_video(video_id):
    db = SessionLocal()
    video = db.query(Video).get(video_id)
    if request.method == "POST":
        video.title = request.form.get("title")
        video.link = request.form.get("link")
        video.form = request.form.get("form")
        db.commit()
        db.close()
        flash("Video updated!", "success")
        return redirect(url_for("admin_dashboard"))
    db.close()
    return render_template("edit_video.html", video=video)

@app.route("/admin/video/delete/<int:video_id>")
@role_required("admin")
def delete_video(video_id):
    db = SessionLocal()
    video = db.query(Video).get(video_id)
    db.delete(video)
    db.commit()
    db.close()
    flash("Video deleted!", "success")
    return redirect(url_for("admin_dashboard"))

# ========================
# ADMIN: Manage Students
# ========================
@app.route("/admin/manage_students")
def manage_students():
    if not session.get("user_id"):
        return redirect(url_for("login"))

    db = SessionLocal()

    # Get search and sort query params
    search_query = request.args.get("search", "").strip().lower()
    sort_by = request.args.get("sort", "id")
    sort_order = request.args.get("order", "asc")

    # Base query
    students = db.query(CompleteProfile)

    # Apply search filter
    if search_query:
        students = students.filter(
            (func.lower(CompleteProfile.first_name).like(f"%{search_query}%")) |
            (func.lower(CompleteProfile.last_name).like(f"%{search_query}%")) |
            (func.lower(CompleteProfile.form).like(f"%{search_query}%")) |
            (func.lower(CompleteProfile.contact_no).like(f"%{search_query}%"))
        )

    # Apply sorting
    sort_column = getattr(CompleteProfile, sort_by, CompleteProfile.id)
    if sort_order == "desc":
        sort_column = sort_column.desc()

    students = students.order_by(sort_column).all()
    db.close()

    return render_template("admin/admin_manage_students.html", students=students, sort_by=sort_by, sort_order=sort_order)

    # =========================
# AJAX ENDPOINTS
# =========================

@app.route("/api/add_item", methods=["POST"])
@role_required("admin")
def add_item():
    data = request.json
    db = SessionLocal()
    try:
        if data["type"] == "live":
            new = LiveClass(
                title=data["title"],
                link=data["link"],
                time=data.get("time"),
                form=data.get("form"),
                subject=data.get("subject"),
                active=data.get("active", False)
            )
        elif data["type"] == "material":
            new = RevisionMaterial(
                title=data["title"],
                link=data["link"],
                form=data.get("form"),
                subject=data.get("subject")
            )
        elif data["type"] == "video":
            new = Video(
                title=data["title"],
                link=data["link"],
                form=data.get("form"),
                subject=data.get("subject")
            )
        db.add(new)
        db.commit()
        return jsonify({"success": True, "id": new.id})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@app.route("/api/update_item/<string:item_type>/<int:item_id>", methods=["PUT"])
@role_required("admin")
def update_item(item_type, item_id):
    data = request.json
    db = SessionLocal()
    try:
        model = {"live": LiveClass, "material": RevisionMaterial, "video": Video}.get(item_type)
        item = db.query(model).get(item_id)
        if not item:
            return jsonify({"success": False, "error": "Not found"}), 404

        for k, v in data.items():
            setattr(item, k, v)
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@app.route("/api/delete_item/<string:item_type>/<int:item_id>", methods=["DELETE"])
@role_required("admin")
def delete_item(item_type, item_id):
    db = SessionLocal()
    try:
        model = {"live": LiveClass, "material": RevisionMaterial, "video": Video}.get(item_type)
        item = db.query(model).get(item_id)
        if not item:
            return jsonify({"success": False, "error": "Not found"}), 404
        db.delete(item)
        db.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.rollback()
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


if __name__ == "__main__":
    app.run(debug=True)
