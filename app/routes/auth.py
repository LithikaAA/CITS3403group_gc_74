import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from werkzeug.utils import secure_filename
from ..models import db, User  # Make sure your User model has set_password and check_password methods

auth_bp = Blueprint('auth', __name__)

# ---------- LOGIN ----------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            # Login logic (if using Flask-Login or manual session)
            return redirect(url_for('dashboard.dashboard'))  # Assuming dashboard is inside dashboard_bp

        flash('Invalid email or password.', 'error')
        return render_template('login.html')  # Rerender with error message

    return render_template('login.html')


# ---------- SIGNUP ----------
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        profile_pic = request.files.get('profile_pic')  # Optional: image upload

        # Check for existing user
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.', 'error')
            return render_template('signup.html')

        # Save profile picture if provided
        pic_filename = None
        if profile_pic:
            filename = secure_filename(profile_pic.filename)
            upload_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            profile_pic.save(upload_path)
            pic_filename = filename

        # Create and store new user
        new_user = User(username=username, email=email, profile_pic=pic_filename)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')
