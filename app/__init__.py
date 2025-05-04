from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
import os   
from config import Config
from dotenv import load_dotenv
from .models import db, User
from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp
from .routes.upload import upload_bp
from .routes.share import share_bp
from .routes.index import index_bp  # Import index blueprint

login_manager = LoginManager()
load_dotenv()

def create_app():
    """
    Factory function to create and configure the Flask app.
    :return: Configured Flask app instance
    """
    # Initialize the Flask app
    app = Flask(__name__)

    # Configure the app
    app.config.from_object(Config)

    app.config['SPOTIPY_CLIENT_ID'] = os.getenv("SPOTIPY_CLIENT_ID")
    app.config['SPOTIPY_CLIENT_SECRET'] = os.getenv("SPOTIPY_CLIENT_SECRET")
    app.config['SPOTIPY_REDIRECT_URI'] = os.getenv("SPOTIPY_REDIRECT_URI")

    # Initialize extensions with the app
    db.init_app(app)
    migrate = Migrate(app, db)

    # Setup LoginManager
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Make current_user available in Jinja templates
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register all blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(upload_bp)
    app.register_blueprint(share_bp)
    app.register_blueprint(index_bp)

    return app
