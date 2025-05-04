# Import necessary modules
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

# Create db object (not bound to app yet)
db = SQLAlchemy()

# ------------------ User Model ------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    profile_pic: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255), default='default_profile.jpg')

    # Add these for account setup
    name: so.Mapped[Optional[str]] = so.mapped_column(sa.String(100))
    gender: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))
    dob: so.Mapped[Optional[datetime.date]] = so.mapped_column(sa.Date)
    mobile: so.Mapped[Optional[str]] = so.mapped_column(sa.String(20))

    # Relationships
    tracks: so.Mapped[List["Track"]] = so.relationship(back_populates='user', cascade="all, delete")
    playlists: so.Mapped[List["Playlist"]] = so.relationship(back_populates='owner', cascade="all, delete")
    shares_sent: so.Mapped[List["Share"]] = so.relationship(
        back_populates="owner",
        foreign_keys="Share.owner_id",
        cascade="all, delete"
    )
    shares_received: so.Mapped[List["Share"]] = so.relationship(
        back_populates="recipient",
        foreign_keys="Share.recipient_id",
        cascade="all, delete"
    )
    shares_visualised: so.Mapped[List["SharedVisualisation"]] = so.relationship(
        back_populates="sharer",
        foreign_keys="SharedVisualisation.shared_by_id",
        cascade="all, delete"
    )
    received_visualised: so.Mapped[List["SharedVisualisation"]] = so.relationship(
        back_populates="recipient",
        foreign_keys="SharedVisualisation.shared_with_id",
        cascade="all, delete"
    )
    shared_data: so.Mapped[List["SharedData"]] = so.relationship(
        back_populates="user",
        cascade="all, delete"
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ------------------ Playlist Model ------------------
class Playlist(db.Model):
    __tablename__ = "playlists"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    owner_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)

    owner: so.Mapped["User"] = so.relationship(back_populates="playlists")
    tracks: so.Mapped[List["Track"]] = so.relationship(back_populates="playlist", cascade="all, delete")
    shares: so.Mapped[List["Share"]] = so.relationship(back_populates="playlist", cascade="all, delete")

    def track_data_as_chart(self):
        genres = [track.genre for track in self.tracks if track.genre]
        counts = {g: genres.count(g) for g in set(genres)}
        return {
            "labels": list(counts.keys()),
            "counts": list(counts.values())
        }


# ------------------ Track Model ------------------
class Track(db.Model):
    __tablename__ = "tracks"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    title: so.Mapped[str] = so.mapped_column(sa.String(100))
    artist: so.Mapped[str] = so.mapped_column(sa.String(100))
    genre: so.Mapped[str] = so.mapped_column(sa.String(50))
    tempo: so.Mapped[float] = so.mapped_column(sa.Float, default=0)
    valence: so.Mapped[float] = so.mapped_column(sa.Float, default=0)
    energy: so.Mapped[float] = so.mapped_column(sa.Float, default=0)
    date_played: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), index=True)
    playlist_id: so.Mapped[Optional[int]] = so.mapped_column(sa.ForeignKey("playlists.id"), nullable=True)

    user: so.Mapped["User"] = so.relationship(back_populates="tracks")
    playlist: so.Mapped[Optional["Playlist"]] = so.relationship(back_populates="tracks")


# ------------------ Share Model ------------------
class Share(db.Model):
    __tablename__ = "shares"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    playlist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("playlists.id"), nullable=False)
    recipient_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    owner_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    playlist: so.Mapped["Playlist"] = so.relationship(back_populates="shares")
    owner: so.Mapped["User"] = so.relationship(back_populates="shares_sent", foreign_keys=[owner_id])
    recipient: so.Mapped["User"] = so.relationship(back_populates="shares_received", foreign_keys=[recipient_id])


# ------------------ SharedVisualisation Model ------------------
class SharedVisualisation(db.Model):
    __tablename__ = "shared_visualisations"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    shared_by_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"))
    shared_with_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"))
    chart_type: so.Mapped[str] = so.mapped_column(sa.String(64))
    timestamp: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    sharer: so.Mapped["User"] = so.relationship(back_populates="shares_visualised", foreign_keys=[shared_by_id])
    recipient: so.Mapped["User"] = so.relationship(back_populates="received_visualised", foreign_keys=[shared_with_id])


# ------------------ SharedData Model ------------------
class SharedData(db.Model):
     __tablename__ = "shared_data"  # Name of the table in the database
 
     # Primary key: Unique identifier for each shared data record
     id: so.Mapped[int] = so.mapped_column(primary_key=True)
 
     # Foreign key linking to User
     user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False, index=True)
 
     # File details
     file_path: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)  # Path to uploaded file
     file_name: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)  # Original file name
     file_type: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)   # File type (e.g., CSV, JSON)
 
     # Timestamp of upload
     timestamp: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)
 
     # Relationship to the User model
     user: so.Mapped['User'] = so.relationship(back_populates="shared_data")  # Link back to User model
