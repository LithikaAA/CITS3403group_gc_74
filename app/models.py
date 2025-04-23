# Import necessary modules
from typing import Optional, List
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

    # Sharing relationships
    shares_sent: so.Mapped[List["SharedVisualisation"]] = so.relationship(
        back_populates="sharer",
        foreign_keys="SharedVisualisation.shared_by_id",
        cascade="all, delete"
    )
    shares_received: so.Mapped[List["SharedVisualisation"]] = so.relationship(
        back_populates="recipient",
        foreign_keys="SharedVisualisation.shared_with_id",
        cascade="all, delete"
    )

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
    __tablename__ = "tracks"  # Name of the table in the database

    # Primary key: unique identifier for each track
    id: so.Mapped[int] = so.mapped_column(primary_key=True)

    # Track metadata fields
    name: so.Mapped[str] = so.mapped_column(sa.String(128))     # Track name
    artist: so.Mapped[str] = so.mapped_column(sa.String(128))   # Artist name
    genre: so.Mapped[str] = so.mapped_column(sa.String(64))     # Genre category
    valence: so.Mapped[float] = so.mapped_column(sa.Float)      # Positivity score (0–1)
    energy: so.Mapped[float] = so.mapped_column(sa.Float)       # Energy level (0–1)
    tempo: so.Mapped[float] = so.mapped_column(sa.Float)        # Tempo (BPM)
    date_played: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow) # When the track was played (default: now)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), index = True) # Foreign key linking this track to the user who listened to it
    user: so.Mapped['User'] = so.relationship(back_populates="tracks") # Relationship to the User model ,this lets you do: track.user to access the parent User object

class SharedVisualisation(db.Model):
    __tablename__ = "shared_visualisations" # Name of the table in the database
 
    id: so.Mapped[int] = so.mapped_column(primary_key=True) # Primary key: Unique identifier for each shared visualisation record
    shared_by_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id")) # ID of the user who shared the visualisation (foreign key to users.id)
    shared_with_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id")) # ID of the user with whom the visualisation is shared (foreign key to users.id)
    chart_type: so.Mapped[str] = so.mapped_column(sa.String(64)) # Type of chart or visualisation that was shared (e.g., 'bar', 'line', 'pie')
    timestamp: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow) # Timestamp of when the visualisation was shared (defaults to current UTC time)

    sharer: so.Mapped["User"] = so.relationship(foreign_keys=[shared_by_id], back_populates="shares_sent") # Relationship to the sharer (user who shared the visualisation) - allows access via: shared_visualisation.sharer
    recipient: so.Mapped["User"] = so.relationship(foreign_keys=[shared_with_id], back_populates="shares_received") # Relationship to the recipient (user with whom the visualisation was shared) - Allows access via: shared_visualisation.recipient
