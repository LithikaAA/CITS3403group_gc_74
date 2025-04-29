from app import db
from app.models import User
from flask import Flask
from config import Config

# Set up the app (since db needs app context)
app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

# Create a user called Charlie
with app.app_context():
    # Check if Charlie already exists
    existing_user = User.query.filter_by(username="charlie").first()
    if not existing_user:
        charlie = User(username="charlie", email="charlie@example.com")
        charlie.set_password("password3")  # Hash and set the password

        db.session.add(charlie)
        db.session.commit()
        print("User 'charlie' created successfully!")
    else:
        print("User 'charlie' already exists.")
