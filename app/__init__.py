# Import necessary modules
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from config import Config
from app.models import db #??
from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp
from .routes.upload import upload_bp
from .routes.share import share_bp


def create_app():
    """
    Factory function to create and configure the Flask app.
    :return: Configured Flask app instance
    """
    # Initialize the Flask app
    app = Flask(__name__)

    # Configure the app
    app.config.from_object(Config)

    # Initialize extensions with the app
    db.init_app(app)

    # Initialise Flask Migrate
    migrate = Migrate(app, db)

    # Register blueprints (e.g., authentication routes)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(share_bp)

    # Define the home route
    @app.route("/")
    def index():
        """
        Render the intro page.
        :return: Rendered HTML for the intro page
        """
        return render_template("index.html")

    return app
