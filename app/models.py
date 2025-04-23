# Import necessary modules
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so 
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing and verification
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Create db object (not bound to app yet)
db = SQLAlchemy()

# Define the User model
class User(db.Model):
    __tablename__ = "users"
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
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))

    tracks: so.Mapped[List["Track"]] = so.relationship(back_populates='user', cascade="all, delete") # when user is deleted, all their tracks are removed

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

class Track(db.Model):
    __tablename__ = "tracks"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(128))
    artist: so.Mapped[str] = so.mapped_column(sa.String(128))
    genre: so.Mapped[str] = so.mapped_column(sa.String(64))
    valence: so.Mapped[float] = so.mapped_column(sa.Float)
    energy: so.Mapped[float] = so.mapped_column(sa.Float)
    tempo: so.Mapped[float] = so.mapped_column(sa.Float)
    date_played: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), index = True)

    user: so.Mapped['User'] = so.relationship(back_populates="tracks")
