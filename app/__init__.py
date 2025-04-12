from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default-secret-key')

    # Import and register blueprints later
    # from .routes.auth import auth_bp
    # app.register_blueprint(auth_bp)

    return app
