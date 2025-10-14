from flask import Flask, render_template, url_for, request, redirect, session, flash
from connections import SessionLocal
from models import User,CompleteProfile
from datetime import datetime

app = Flask(__name__)
app.secret_key = "silaswanyamarechosilasayangaamukowaivansamuel"  

@app.route('/')
def home():
    return redirect(url_for('login'))


# ✅ LOGIN
@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""
    if request.method == 'POST':
        db = SessionLocal()
        username = request.form['username']
        password = request.form['password']
        user = db.query(User).filter_by(username=username, password=password).first()
        db.close()

        if user:
            session['user_id'] = user.id
            return redirect(url_for('complete_profile'))
        else:
            message = "Invalid username or password"
    return render_template('login.html', message=message)


# ✅ REGISTER
@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        if password != confirm_password:
            message = "Passwords do not match"
            return render_template('register.html', message=message)
        else:
            db = SessionLocal()
            existing_user = db.query(User).filter_by(username=username).first()

            if existing_user:
                message = "Username already exists"
                db.close()
                return render_template('register.html', message=message)
            else:
                new_user = User(username=username, password=password)
                db.add(new_user)
                db.commit()
                db.close()
                # Redirect to login after successful registration
                return redirect(url_for('login'))

    return render_template('register.html', message=message)



# ✅ FORGOT PASSWORD
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
                user.password = new_password
                db.commit()
                message = "Password updated successfully! You can now log in."
            else:
                message = "User not found."
            db.close()
            return redirect(url_for('login'))
    return render_template('reset_password.html', message=message, username=username)

# ---------- COMPLETE PROFILE ----------
@app.route('/complete_profile', methods=['GET', 'POST'])
def complete_profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = SessionLocal()
    user = db.query(User).filter_by(id=session['user_id']).first()

    if not user:
        db.close()
        return redirect(url_for('login'))

    # Check if profile exists
    profile = user.profile

    if request.method == 'POST':
        first_name = request.form['first_name']
        middle_name = request.form.get('middle_name')
        last_name = request.form['last_name']
        contact_no = request.form['contact_no']
        guardian_name = request.form['guardian_name']
        form_selected = request.form['form']

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
            profile =CompleteProfile(
                user_id=user.id,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                contact_no=contact_no,
                guardian_name=guardian_name,
                form=form_selected
            )
            db.add(profile)

        db.commit()
        db.close()
        return redirect(url_for('dashboard'))

    # Pre-fill form if profile exists
    profile_data = profile.__dict__ if profile else {}
    db.close()
    return render_template('students/complete_profile.html', profile=profile_data)

# ---------- DASHBOARD ----------
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db = SessionLocal()
    user = db.query(User).filter_by(id=session['user_id']).first()

    if not user:
        db.close()
        return redirect(url_for('login'))

    profile = user.profile
    if not profile:
        db.close()
        return redirect(url_for('complete_profile'))

    # Prepare student data
    student_data = {
        'full_name': f"{profile.first_name} {profile.middle_name or ''} {profile.last_name}".strip(),
        'form': profile.form,
        'phone': profile.contact_no,
        'guardian_name': profile.guardian_name
    }

    # Example sections (replace with real queries)
    live_classes = []          # Query LiveClass table filtering by profile.form
    revision_materials = []    # Query RevisionMaterial table filtering by profile.form
    videos = []                # Query Video table filtering by profile.form

    db.close()

    return render_template(
        'students/student_dashboard.html',
        student=student_data,
        live_classes=live_classes,
        revision_materials=revision_materials,
        videos=videos
    )


# ✅ LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)
