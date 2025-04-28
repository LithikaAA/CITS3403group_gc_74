
from ..models import db, User  # Import database and User model

import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify, session
from werkzeug.utils import secure_filename


auth_bp = Blueprint('auth', __name__)

# ---------- LOGIN ----------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):

            # Store user information in the session
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard.dashboard'))  # Redirect to dashboard
        else:
            flash('Invalid email or password.', 'error')
            return redirect(url_for('auth.login'))

    return render_template('login.html')


# ---------- SIGNUP ----------
@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        profile_pic = request.files.get('profile_pic')

        # Check if username or email already exists
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.', 'error')
            return render_template('signup.html')

        # Handle profile picture upload
        pic_filename = None
        if profile_pic and profile_pic.filename != '':
            filename = secure_filename(profile_pic.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            profile_pic.save(os.path.join(upload_folder, filename))
            pic_filename = filename

        # Create new user
        new_user = User(username=username, email=email, profile_pic=pic_filename)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


# ---------- TERMS ----------
@auth_bp.route('/terms')
def terms():
    return render_template('terms.html')

# ---------- ACCOUNT SETUP ----------
@auth_bp.route('/account-setup', methods=['GET', 'POST'])
def account_setup():
    if request.method == 'POST':
        # Here you would normally process form data, e.g.:
        name = request.form.get('name')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        email = request.form.get('email')
        mobile = request.form.get('mobile')

        # For now, just flash success and redirect
        flash(f'Account setup completed for {name}!', 'success')
        return redirect(url_for('dashboard.dashboard'))

    return render_template('account_setup.html')


@auth_bp.route('/logout')
def logout():
    """
    Log the user out by clearing the session.
    """
    session.clear()
    return redirect(url_for('auth.login'))
