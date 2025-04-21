from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# You can import routes later here
from .routes import auth  # only if you’ve made this file already
from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite')
    
    # Initialize extensions (add these later)
    # db.init_app(app)
    # login_manager.init_app(app)
    
    # Register blueprints
    from .routes.auth import auth_bp  # Changed to auth_bp for consistency
    app.register_blueprint(auth_bp, url_prefix='/')
    
    return app

# This allows you to still import app directly if needed
app = create_app()
