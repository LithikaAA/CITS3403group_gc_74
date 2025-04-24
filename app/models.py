# Import necessary modules
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy for database ORM
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing and verification

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# Define the User model
class User(db.Model):
    """
    User model to represent users in the database.
    """
    # Primary key: Unique identifier for each user
    id = db.Column(db.Integer, primary_key=True)

    # Username: Must be unique and cannot be null
    username = db.Column(db.String(80), unique=True, nullable=False)

    # Email: Must be unique and cannot be null
    email = db.Column(db.String(120), unique=True, nullable=False)

    # Password hash: Stores the hashed version of the user's password
    password_hash = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        """
        Hashes the password and stores it in the password_hash field.
        :param password: Plaintext password provided by the user.
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifies the provided password against the stored hash.
        :param password: Plaintext password to verify.
        :return: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)