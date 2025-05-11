import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
from werkzeug.utils import secure_filename
from flask_login import login_user, logout_user, current_user, login_required
from ..models import db, User
from datetime import datetime

auth_bp = Blueprint('auth', __name__)

# ---------- LOGIN ----------
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form.get('identifier')  # username OR email
        password = request.form.get('password')

        # Match by either username or email
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()

        if user and user.check_password(password):
            login_user(user)  # Flask-Login session
            session['user_id'] = user.id
            session['username'] = user.username
            flash('Logged in successfully!', 'success')
            return redirect(url_for('dashboard.dashboard'))

        flash('Invalid username/email or password.', 'error')
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

        # Check for existing user
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.', 'error')
            return render_template('signup.html')

        # Handle profile picture upload
        pic_filename = None
        if profile_pic and profile_pic.filename:
            filename = secure_filename(profile_pic.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            profile_pic.save(os.path.join(upload_folder, filename))
            pic_filename = filename

        # Create user
        new_user = User(username=username, email=email, profile_pic=pic_filename)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


# ---------- CHANGE PASSWORD ----------
@auth_bp.route('/change-password', methods=['POST'])
@login_required
def change_password():
    current_pw = request.form.get('current_password')
    new_pw = request.form.get('new_password')
    confirm_pw = request.form.get('confirm_password')

    if not current_user.check_password(current_pw):
        flash('Current password is incorrect.', 'error')
        return redirect(url_for('auth.account_setup'))

    if new_pw != confirm_pw:
        flash("New passwords don't match.", 'error')
        return redirect(url_for('auth.account_setup'))

    current_user.set_password(new_pw)
    db.session.commit()
    flash('Password updated successfully!', 'success')
    return redirect(url_for('auth.account_setup'))


# ---------- LOGOUT ----------
@auth_bp.route('/logout')
def logout():
    """
    Log the user out by clearing both Flask-Login and manual session data.
    """
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))


# ---------- TERMS ----------
@auth_bp.route('/terms')
def terms():
    return render_template('terms.html')


# ---------- ACCOUNT SETUP ----------
@auth_bp.route('/account-setup', methods=['GET', 'POST'])
@login_required
def account_setup():
    if request.method == 'POST':
        new_username = request.form.get('username')
        name = request.form.get('name')
        gender = request.form.get('gender')
        dob_str = request.form.get('dob')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        profile_pic = request.files.get('profile_pic')

        # Check if username is already taken (but only if changed)
        if new_username != current_user.username and User.query.filter_by(username=new_username).first():
            flash('That username is already taken.', 'error')
            return render_template('account_setup.html')

        # Update user info
        current_user.username = new_username
        current_user.name = name
        current_user.gender = gender
        current_user.email = email
        current_user.mobile = mobile

        # Handle date of birth properly
        if dob_str:
            try:
                current_user.dob = datetime.strptime(dob_str, '%Y-%m-%d').date()
            except ValueError:
                flash('Invalid date format for Date of Birth.', 'error')
                return render_template('account_setup.html')

        # Handle profile picture upload
        if profile_pic and profile_pic.filename:
            filename = secure_filename(profile_pic.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            profile_pic.save(os.path.join(upload_folder, filename))
            current_user.profile_pic = filename

        db.session.commit()
        flash('Account updated successfully!', 'success')
        return redirect(url_for('auth.account_setup'))

    return render_template('account_setup.html')