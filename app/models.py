# Import necessary modules
from typing import Optional, List
import sqlalchemy as sa
import sqlalchemy.orm as so
from sqlalchemy.orm import Mapped, mapped_column, relationship
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import ForeignKey

# Create db object (not bound to app yet)
db = SQLAlchemy()

# ------------------ User Model ------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(120), index=True, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(sa.String(256))
    profile_pic: Mapped[Optional[str]] = mapped_column(sa.String(255), default='default_profile.jpg')
    tracks: Mapped[List["Track"]] = relationship("Track", back_populates="user")

    # Add these for account setup
    name: Mapped[Optional[str]] = mapped_column(sa.String(100))
    gender: Mapped[Optional[str]] = mapped_column(sa.String(20))
    dob: Mapped[Optional[datetime.date]] = mapped_column(sa.Date)
    mobile: Mapped[Optional[str]] = mapped_column(sa.String(20))

    # Relationships
    playlists: Mapped[List["Playlist"]] = relationship(back_populates='owner', cascade="all, delete")
    shares_sent: Mapped[List["Share"]] = relationship(back_populates="owner", foreign_keys="Share.owner_id", cascade="all, delete")
    shares_received: Mapped[List["Share"]] = relationship(back_populates="recipient", foreign_keys="Share.recipient_id", cascade="all, delete")
    shares_visualised: Mapped[List["SharedVisualisation"]] = relationship(back_populates="sharer", foreign_keys="SharedVisualisation.shared_by_id", cascade="all, delete")
    received_visualised: Mapped[List["SharedVisualisation"]] = relationship(back_populates="recipient", foreign_keys="SharedVisualisation.shared_with_id", cascade="all, delete")
    shared_data: Mapped[List["SharedData"]] = relationship(back_populates="user", cascade="all, delete")

    friends = relationship(
        "User",
        secondary="friend",
        primaryjoin="User.id==Friend.user_id",
        secondaryjoin="User.id==Friend.friend_id",
        backref="friend_of"
    )

    user_tracks: Mapped[List["UserTrack"]] = relationship(back_populates="user", cascade="all, delete")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def incoming_friend_requests(self):
        return Friend.query.filter_by(friend_id=self.id, is_accepted=False).all()

    def sent_friend_requests(self):
        return Friend.query.filter_by(user_id=self.id, is_accepted=False).all()

    def friends_list(self):
        sent = Friend.query.filter_by(user_id=self.id, is_accepted=True).all()
        received = Friend.query.filter_by(friend_id=self.id, is_accepted=True).all()
        return [f.friend for f in sent] + [f.user for f in received]


# ------------------ Friend Model ------------------
class Friend(db.Model):
    __tablename__ = 'friend'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    friend_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    is_accepted = db.Column(db.Boolean, default=False)

    user = db.relationship('User', foreign_keys=[user_id], backref='friend_requests_sent')
    friend = db.relationship('User', foreign_keys=[friend_id], backref='friend_requests_received')


# ------------------ Playlist Model ------------------
class Playlist(db.Model):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: Mapped["User"] = relationship(back_populates="playlists")
    shares: Mapped[List["Share"]] = relationship(back_populates="playlist", cascade="all, delete")

    def track_data_as_chart(self):
        genres = [track.genre for track in self.tracks if track.genre]
        counts = {g: genres.count(g) for g in set(genres)}
        return {"labels": list(counts.keys()), "counts": list(counts.values())}


# ------------------ Track Model ------------------
class Track(db.Model):
    __tablename__ = "tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(sa.String(100))
    artist: Mapped[str] = mapped_column(sa.String(100))
    genre: Mapped[str] = mapped_column(sa.String(50))
    tempo: Mapped[float] = mapped_column(sa.Float, default=0)
    valence: Mapped[float] = mapped_column(sa.Float, default=0)
    energy: Mapped[float] = mapped_column(sa.Float, default=0)
    date_played: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    acousticness: Mapped[float] = mapped_column(sa.Float, default=0)
    liveness: Mapped[float] = mapped_column(sa.Float, default=0)
    danceability: Mapped[float] = mapped_column(sa.Float, default=0)
    mode: Mapped[int] = mapped_column(sa.Integer, default=1)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    user: Mapped["User"] = relationship(back_populates="tracks")
    user_tracks: Mapped[List["UserTrack"]] = relationship(back_populates="track", cascade="all, delete")


# ------------------ UserTrack Model ------------------
class UserTrack(db.Model):
    __tablename__ = "user_tracks"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    track_id: Mapped[int] = mapped_column(ForeignKey("tracks.id"), nullable=False)

    song: Mapped[str] = mapped_column(sa.String(100))
    artist: Mapped[str] = mapped_column(sa.String(100))
    song_duration: Mapped[int] = mapped_column(sa.Integer)
    times_played: Mapped[int] = mapped_column(sa.Integer, default=0)
    total_ms_listened: Mapped[int] = mapped_column(sa.Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="user_tracks")
    track: Mapped["Track"] = relationship(back_populates="user_tracks")


# ------------------ Share Model ------------------
class Share(db.Model):
    __tablename__ = "shares"

    id: Mapped[int] = mapped_column(primary_key=True)
    playlist_id: Mapped[int] = mapped_column(ForeignKey("playlists.id"), nullable=False)
    recipient_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    playlist: Mapped["Playlist"] = relationship(back_populates="shares")
    owner: Mapped["User"] = relationship(back_populates="shares_sent", foreign_keys=[owner_id])
    recipient: Mapped["User"] = relationship(back_populates="shares_received", foreign_keys=[recipient_id])


# ------------------ SharedVisualisation Model ------------------
class SharedVisualisation(db.Model):
    __tablename__ = "shared_visualisations"

    id: Mapped[int] = mapped_column(primary_key=True)
    shared_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    shared_with_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    chart_type: Mapped[str] = mapped_column(sa.String(64))
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    sharer: Mapped["User"] = relationship(back_populates="shares_visualised", foreign_keys=[shared_by_id])
    recipient: Mapped["User"] = relationship(back_populates="received_visualised", foreign_keys=[shared_with_id])



# ------------------ SharedData Model ------------------
class SharedData(db.Model):
    __tablename__ = "shared_data"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(sa.String(255), nullable=False)  # Path to uploaded file
    file_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)  # Original file name
    file_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)   # File type (e.g., CSV, JSON)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="shared_data")  # Link back to User model