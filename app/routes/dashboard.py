from flask import Blueprint, render_template, session, redirect, url_for

# Create a blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    """
    Render the user dashboard.
    """
    if 'user_id' not in session:
        # Redirect to login if the user is not logged in
        return redirect(url_for('auth.login'))

    # Debugging: Print session data
    print("Session data:", session)

    return render_template('dashboard.html', username=session.get('username'))