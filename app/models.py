# Import necessary modules
from flask_sqlalchemy import SQLAlchemy  # SQLAlchemy for database ORM
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash  # For password hashing and verification
import os
from datetime import datetime

# Initialize the SQLAlchemy instance
db = SQLAlchemy()

# ------------------ User Model ------------------
class User(UserMixin, db.Model):
    __tablename__ = 'user'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80), unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    profile_pic   = db.Column(db.String(128), nullable=True, default='default_profile.jpg')

    playlists       = db.relationship('Playlist', backref='owner', lazy=True)
    shares_sent     = db.relationship('Share', foreign_keys='Share.owner_id', backref='owner', lazy=True)
    shares_received = db.relationship('Share', foreign_keys='Share.recipient_id', backref='recipient', lazy=True)
    shared_data     = db.relationship('SharedData', backref='user', lazy=True)  # added relation to SharedData

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """
        Verifies the provided password against the stored hash.
        :param password: Plaintext password to verify.
        :return: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password_hash, password)

# ------------------ Playlist Model ------------------
class Playlist(db.Model):
    __tablename__ = 'playlist'

    id        = db.Column(db.Integer, primary_key=True)
    name      = db.Column(db.String(100), nullable=False)
    owner_id  = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    tracks    = db.relationship('Track', backref='playlist', lazy=True)
    shares    = db.relationship('Share', backref='playlist', lazy=True)

    def track_data_as_chart(self):
        genres = [track.genre for track in self.tracks if track.genre]
        counts = {g: genres.count(g) for g in set(genres)}
        return {
            "labels": list(counts.keys()),
            "counts": list(counts.values())
        }

# ------------------ Track Model ------------------
class Track(db.Model):
    __tablename__ = 'track'

    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(100))
    artist      = db.Column(db.String(100))
    genre       = db.Column(db.String(50))
    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)

# ------------------ Share Model ------------------
class Share(db.Model):
    __tablename__ = 'share'

    id           = db.Column(db.Integer, primary_key=True)
    playlist_id  = db.Column(db.Integer, db.ForeignKey('playlist.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    owner_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp    = db.Column(db.DateTime, default=datetime.utcnow)

# ------------------ SharedData Model ------------------
class SharedData(db.Model):
    """
    Model to represent shared Spotify data.
    """
    __tablename__ = 'shared_data'

    id = db.Column(db.Integer, primary_key=True)  # Unique identifier
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Foreign key to User
    file_path = db.Column(db.String(255), nullable=False)  # Path to the uploaded file
    file_name = db.Column(db.String(255), nullable=False)  # Original file name
    file_type = db.Column(db.String(50), nullable=False)  # File type (e.g., CSV, JSON)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Timestamp for when the file was uploaded
