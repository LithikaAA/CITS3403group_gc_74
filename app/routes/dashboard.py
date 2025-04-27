from flask import Blueprint, render_template
from app.models import User
# Create a blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    """
    Render the user dashboard.
    :return: Rendered dashboard page
    """
    return render_template('dashboard.html')

@dashboard_bp.route('/test-data')
def test_data():
    users = User.query.all()
    return render_template('test_data.html', users=users)