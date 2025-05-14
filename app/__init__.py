import os
from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from config import Config
from dotenv import load_dotenv
from .models import db, User
from flask_wtf.csrf import CSRFProtect, generate_csrf

# Import all blueprints
from .routes.auth import auth_bp
from .routes.dashboard import dashboard_bp
from .routes.upload import upload_bp
from .routes.share import share_bp
from .routes.index import index_bp
from .routes.friends import friends_bp

# Load environment variables
load_dotenv()

login_manager = LoginManager()
csrf = CSRFProtect()

def create_app(config_class=Config):
    """
    Factory function to create and configure the Flask app.
    :return: Configured Flask app instance
    """
    app = Flask(__name__, instance_relative_config=True)

    # Load configuration
    app.config.from_object(config_class)

    # Initialise CSRF protection
    csrf.init_app(app)
    app.jinja_env.globals['csrf_token'] = generate_csrf

    # Optionally include Spotify credentials in config
    app.config.setdefault('SPOTIPY_CLIENT_ID', os.getenv("SPOTIPY_CLIENT_ID"))
    app.config.setdefault('SPOTIPY_CLIENT_SECRET', os.getenv("SPOTIPY_CLIENT_SECRET"))
    app.config.setdefault('SPOTIPY_REDIRECT_URI', os.getenv("SPOTIPY_REDIRECT_URI"))
    
    # Initialise extensions
    db.init_app(app)
    Migrate(app, db)

    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(upload_bp)  # includes Spotify API routes now
    app.register_blueprint(share_bp)
    app.register_blueprint(friends_bp)
    app.register_blueprint(index_bp)

    return app