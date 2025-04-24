from flask import Blueprint, render_template, request, redirect, url_for, jsonify  # Flask utilities for routing and rendering
from ..models import db, User  # Import database and User model

# Create a blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Handle user login.
    :return: Rendered login page or redirect to dashboard on successful login
    """
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Query the database for the user
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            return redirect(url_for('dashboard'))  # Redirect to dashboard on successful login
        return jsonify({'error': 'Invalid credentials'}), 401

    return render_template('login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Handle user registration.
    :return: Rendered signup page or redirect to login on successful registration
    """
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Check if the user already exists
        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({'error': 'User already exists'}), 400

        # Create a new user
        new_user = User(username=username, email=email)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))  # Redirect to login page after successful signup

    return render_template('signup.html')