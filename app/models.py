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
    user_tracks: so.Mapped[List["UserTrack"]] = so.relationship(
        back_populates="user", cascade="all, delete"
    )
    
    # Keep the direct relationship to the Friend model
    friend_requests_sent: so.Mapped[List["Friend"]] = so.relationship(
        "Friend",
        back_populates="user",
        foreign_keys="Friend.user_id",
    )
    
    friend_requests_received: so.Mapped[List["Friend"]] = so.relationship(
        "Friend",
        back_populates="friend",
        foreign_keys="Friend.friend_id",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    # Friend helper methods
    def incoming_friend_requests(self):
        return Friend.query.filter_by(friend_id=self.id, is_accepted=False).all()
    
    def sent_friend_requests(self):
        return Friend.query.filter_by(user_id=self.id, is_accepted=False).all()
    
    def friends_list(self):
        """Returns a list of User objects who are friends with this user"""
        sent = Friend.query.filter_by(user_id=self.id, is_accepted=True).all()
        received = Friend.query.filter_by(friend_id=self.id, is_accepted=True).all()
        return [f.friend for f in sent] + [f.user for f in received]
    
    # Keep the method for backward compatibility
    def friends(self):
        """Method version - maintain for backward compatibility"""
        return self.friends_list()
    
    # Add a property for easier access in templates
    @property
    def all_friends(self):
        """Property for convenient access to friends list in templates"""
        return self.friends_list()
        
    # Calculate average BPM for a user based on their tracks
    @property
    def average_bpm(self):
        from sqlalchemy.sql import func
        result = db.session.query(func.avg(Track.tempo)) \
            .join(UserTrack, UserTrack.track_id == Track.id) \
            .filter(UserTrack.user_id == self.id) \
            .scalar()
        return result or 0


# ------------------ Friend Model ------------------
class Friend(db.Model):
    __tablename__ = "friend"
    
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    friend_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    is_accepted: so.Mapped[bool] = so.mapped_column(sa.Boolean, default=False)
    
    # Fixed relationships to avoid the overlaps warning
    user: so.Mapped["User"] = so.relationship(
        "User", 
        foreign_keys=[user_id], 
        back_populates="friend_requests_sent"
    )
    
    friend: so.Mapped["User"] = so.relationship(
        "User", 
        foreign_keys=[friend_id], 
        back_populates="friend_requests_received"
    )


# ------------------ Playlist Model ------------------
class Playlist(db.Model):
    __tablename__ = "playlists"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    owner_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)

    owner: so.Mapped["User"] = so.relationship(back_populates="playlists")
    shares: so.Mapped[List["Share"]] = so.relationship(back_populates="playlist", cascade="all, delete")
    playlist_tracks: so.Mapped[List["PlaylistTrack"]] = so.relationship(back_populates="playlist", cascade="all, delete")
    tracks: so.Mapped[List["Track"]] = so.relationship(
        secondary="playlist_tracks",
        back_populates="playlists",
        viewonly=True
    )

    def track_data_as_chart(self):
        genres = [track.genre for track in self.tracks if track.genre]
        counts = {g: genres.count(g) for g in set(genres)}
        return {
            "labels": list(counts.keys()),
            "counts": list(counts.values())
        }


# ------------------ PlaylistTrack Join Table ------------------
class PlaylistTrack(db.Model):
    __tablename__ = "playlist_tracks"

    playlist_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("playlists.id"), primary_key=True)
    track_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("tracks.id"), primary_key=True)

    playlist: so.Mapped["Playlist"] = so.relationship(back_populates="playlist_tracks")
    track: so.Mapped["Track"] = so.relationship()


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
    acousticness: so.Mapped[float] = so.mapped_column(sa.Float, default=0)
    liveness: so.Mapped[float] = so.mapped_column(sa.Float, default=0)
    danceability: so.Mapped[float] = so.mapped_column(sa.Float, default=0)
    mode: so.Mapped[str] = so.mapped_column(sa.String(20), default="Major")
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)

    user: so.Mapped["User"] = so.relationship(foreign_keys=[user_id])
    user_tracks: so.Mapped[List["UserTrack"]] = so.relationship(
        back_populates="track", cascade="all, delete"
    )
    playlists: so.Mapped[List["Playlist"]] = so.relationship(
        secondary="playlist_tracks",
        back_populates="tracks",
        viewonly=True
    )


# ------------------ UserTrack Model ------------------
class UserTrack(db.Model):
    __tablename__ = "user_tracks"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False)
    track_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("tracks.id"), nullable=False)
    song: so.Mapped[str] = so.mapped_column(sa.String(100))
    artist: so.Mapped[str] = so.mapped_column(sa.String(100))
    song_duration: so.Mapped[int] = so.mapped_column(sa.Integer)
    times_played: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)
    total_ms_listened: so.Mapped[int] = so.mapped_column(sa.Integer, default=0)

    user: so.Mapped["User"] = so.relationship(back_populates="user_tracks")
    track: so.Mapped["Track"] = so.relationship(back_populates="user_tracks")


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
    __tablename__ = "shared_data"

    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False, index=True)
    file_path: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    file_name: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    file_type: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    user: so.Mapped['User'] = so.relationship(back_populates="shared_data")