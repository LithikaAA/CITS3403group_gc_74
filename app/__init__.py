from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()  # Loads variables from .env

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# You can import routes later here
from .routes import auth  # only if you’ve made this file already

