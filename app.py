from flask import Flask, render_template, url_for, request, redirect, session, flash
from connections import SessionLocal
from models import User

app = Flask(__name__)
app.secret_key = "silaswanyamarechosilasayangaamukowaivansamuel"  


# ✅ Redirect users to login page (home route)
@app.route('/')
def home():
    return redirect(url_for('login'))


# ✅ Example login route (optional placeholder)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        db = SessionLocal()
        username = request.form['username']
        password = request.form['password']
        user = db.query(User).filter_by(username=username, password=password).first()
        db.close()

        if user:
            session['user_id'] = user.id
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')


# ✅ Dashboard route (example)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first", "warning")
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/forgot_password')
def forgot_password():
    return render_template('forgot_password.html')


# ✅ Log out users
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully", "info")
    return redirect(url_for("login"))


if __name__ == '__main__':
    app.run(debug=True)
