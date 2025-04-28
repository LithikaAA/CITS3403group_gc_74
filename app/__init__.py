from flask import Flask
from .models import db  # Import db from models
from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp
from .routes.upload import upload_bp
from .routes.share import share_bp
from .routes.index import index_bp  # Import index blueprint

def create_app():
    """
    Factory function to create and configure the Flask app.
    :return: Configured Flask app instance
    """
    # Initialize the Flask app
    app = Flask(__name__)

    # Configure the app
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vibeshare.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'your_secret_key'

    # Initialize extensions with the app
    db.init_app(app)

    # Register all blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(upload_bp)
    app.register_blueprint(share_bp)
    app.register_blueprint(index_bp)  # Register index blueprint

    return app