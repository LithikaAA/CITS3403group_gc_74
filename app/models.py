# Import necessary modules
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so 
from app import db
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing and verification
from datetime import datetime

# Define the User model
class User(db.Model):
    """
    User model to represent users in the database.
    """
    # Primary key: Unique identifier for each user
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Username: Must be unique and cannot be null
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)

    # Email: Must be unique and cannot be null
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique= True)

    # Password hash: Stores the hashed version of the user's password
    passwrod_has: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

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

