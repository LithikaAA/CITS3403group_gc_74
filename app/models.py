from typing import Optional, List
import sqlalchemy as sa
from sqlalchemy.orm import Mapped, mapped_column, relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, date

db = SQLAlchemy()

# ------------------ User Model ------------------
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(sa.String(64), index=True, unique=True)
    email: Mapped[str] = mapped_column(sa.String(120), index=True, unique=True)
    password_hash: Mapped[Optional[str]] = mapped_column(sa.String(256))
    profile_pic: Mapped[Optional[str]] = mapped_column(sa.String(255), default='default_profile.jpg')

    # Account setup
    name: Mapped[Optional[str]] = mapped_column(sa.String(100))
    gender: Mapped[Optional[str]] = mapped_column(sa.String(20))
    dob: Mapped[Optional[date]] = mapped_column(sa.Date)
    mobile: Mapped[Optional[str]] = mapped_column(sa.String(20))

<<<<<<< HEAD
    # Relationships
    playlists: Mapped[List["Playlist"]] = relationship(back_populates='owner', cascade="all, delete")
    shares_sent: Mapped[List["Share"]] = relationship(back_populates="owner", foreign_keys="Share.owner_id", cascade="all, delete")
    shares_received: Mapped[List["Share"]] = relationship(back_populates="recipient", foreign_keys="Share.recipient_id", cascade="all, delete")
    shares_visualised: Mapped[List["SharedVisualisation"]] = relationship(back_populates="sharer", foreign_keys="SharedVisualisation.shared_by_id", cascade="all, delete")
    received_visualised: Mapped[List["SharedVisualisation"]] = relationship(back_populates="recipient", foreign_keys="SharedVisualisation.shared_with_id", cascade="all, delete")
    shared_data: Mapped[List["SharedData"]] = relationship(back_populates="user", cascade="all, delete")
    user_tracks: Mapped[List["UserTrack"]] = relationship(back_populates="user", cascade="all, delete")

    friends = relationship(
        "User",
        secondary="friend",
        primaryjoin="User.id==Friend.user_id",
        secondaryjoin="User.id==Friend.friend_id",
        backref="friend_of"
=======
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
>>>>>>> 1ebfa4c23a28ca24835c8da78ec76b5cbcd2e666
    )

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

    user = relationship('User', foreign_keys=[user_id], backref='friend_requests_sent')
    friend = relationship('User', foreign_keys=[friend_id], backref='friend_requests_received')


# ------------------ Playlist Model ------------------
class Playlist(db.Model):
    __tablename__ = "playlists"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(sa.String(100), nullable=False)
    owner_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"), nullable=False)

<<<<<<< HEAD
    owner: Mapped["User"] = relationship(back_populates="playlists")
    shares: Mapped[List["Share"]] = relationship(back_populates="playlist", cascade="all, delete")
    playlist_tracks: Mapped[List["PlaylistTrack"]] = relationship(back_populates="playlist", cascade="all, delete")
    tracks: Mapped[List["Track"]] = relationship(secondary="playlist_tracks", back_populates="playlists", viewonly=True)
=======
    owner: so.Mapped["User"] = so.relationship(back_populates="playlists")
    shares: so.Mapped[List["Share"]] = so.relationship(back_populates="playlist", cascade="all, delete")
    playlist_tracks: so.Mapped[List["PlaylistTrack"]] = so.relationship(back_populates="playlist", cascade="all, delete")
    tracks: so.Mapped[List["Track"]] = so.relationship(
        secondary="playlist_tracks",
        back_populates="playlists",
        viewonly=True
    )
>>>>>>> 1ebfa4c23a28ca24835c8da78ec76b5cbcd2e666

    def track_data_as_chart(self):
        genres = [track.genre for track in self.tracks if track.genre]
        counts = {g: genres.count(g) for g in set(genres)}
        return {"labels": list(counts.keys()), "counts": list(counts.values())}


# ------------------ PlaylistTrack Join Table ------------------
class PlaylistTrack(db.Model):
    __tablename__ = "playlist_tracks"

    playlist_id: Mapped[int] = mapped_column(sa.ForeignKey("playlists.id"), primary_key=True)
    track_id: Mapped[int] = mapped_column(sa.ForeignKey("tracks.id"), primary_key=True)

    playlist: Mapped["Playlist"] = relationship(back_populates="playlist_tracks")
    track: Mapped["Track"] = relationship()


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

<<<<<<< HEAD
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

    user_tracks: Mapped[List["UserTrack"]] = relationship(back_populates="track", cascade="all, delete")
    playlists: Mapped[List["Playlist"]] = relationship(secondary="playlist_tracks", back_populates="tracks", viewonly=True)
=======
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
    mode: so.Mapped[int] = so.mapped_column(sa.Integer, default=1)

    user_tracks: so.Mapped[List["UserTrack"]] = so.relationship(
        back_populates="track", cascade="all, delete"
    )
    playlists: so.Mapped[List["Playlist"]] = so.relationship(
        secondary="playlist_tracks",
        back_populates="tracks",
        viewonly=True
    )
>>>>>>> 1ebfa4c23a28ca24835c8da78ec76b5cbcd2e666


# ------------------ UserTrack Model ------------------
class UserTrack(db.Model):
    __tablename__ = "user_tracks"

<<<<<<< HEAD
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"), nullable=False)
    track_id: Mapped[int] = mapped_column(sa.ForeignKey("tracks.id"), nullable=False)

    song: Mapped[str] = mapped_column(sa.String(100))
    artist: Mapped[str] = mapped_column(sa.String(100))
    song_duration: Mapped[int] = mapped_column(sa.Integer)
    times_played: Mapped[int] = mapped_column(sa.Integer, default=0)
    total_ms_listened: Mapped[int] = mapped_column(sa.Integer, default=0)

    user: Mapped["User"] = relationship(back_populates="user_tracks")
    track: Mapped["Track"] = relationship(back_populates="user_tracks")

=======
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
>>>>>>> 1ebfa4c23a28ca24835c8da78ec76b5cbcd2e666


# ------------------ Share Model ------------------
class Share(db.Model):
    __tablename__ = "shares"

    id: Mapped[int] = mapped_column(primary_key=True)
    playlist_id: Mapped[int] = mapped_column(sa.ForeignKey("playlists.id"), nullable=False)
    recipient_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"), nullable=False)
    owner_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    playlist: Mapped["Playlist"] = relationship(back_populates="shares")
    owner: Mapped["User"] = relationship(back_populates="shares_sent", foreign_keys=[owner_id])
    recipient: Mapped["User"] = relationship(back_populates="shares_received", foreign_keys=[recipient_id])


# ------------------ SharedVisualisation Model ------------------
class SharedVisualisation(db.Model):
    __tablename__ = "shared_visualisations"

    id: Mapped[int] = mapped_column(primary_key=True)
    shared_by_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))
    shared_with_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"))
    chart_type: Mapped[str] = mapped_column(sa.String(64))
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    sharer: Mapped["User"] = relationship(back_populates="shares_visualised", foreign_keys=[shared_by_id])
    recipient: Mapped["User"] = relationship(back_populates="received_visualised", foreign_keys=[shared_with_id])


# ------------------ SharedData Model ------------------
class SharedData(db.Model):
    __tablename__ = "shared_data"

<<<<<<< HEAD
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey("users.id"), nullable=False, index=True)
    file_path: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    file_name: Mapped[str] = mapped_column(sa.String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(sa.String(50), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    user: Mapped["User"] = relationship(back_populates="shared_data")
=======
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey("users.id"), nullable=False, index=True)
    file_path: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    file_name: so.Mapped[str] = so.mapped_column(sa.String(255), nullable=False)
    file_type: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    timestamp: so.Mapped[datetime] = so.mapped_column(default=datetime.utcnow)

    user: so.Mapped['User'] = so.relationship(back_populates="shared_data")
>>>>>>> 1ebfa4c23a28ca24835c8da78ec76b5cbcd2e666
