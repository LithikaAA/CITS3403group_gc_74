from flask import Blueprint, render_template

# Create a blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard')
def dashboard():
    """
    Render the user dashboard.
    :return: Rendered dashboard page
    """
    return render_template('dashboard.html')