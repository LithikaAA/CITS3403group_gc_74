from app import create_app, db
from app.models import User, Playlist, Track, PlaylistTrack, Friend, UserTrack, Share
from werkzeug.security import generate_password_hash
from datetime import datetime
import pandas as pd
import random

spotify_df = pd.read_csv("spotify.csv")
spotify_df.rename(columns={"artists": "artist", "track_genre": "genre"}, inplace=True)
spotify_df = spotify_df.dropna(subset=["track_name", "artist", "genre", "tempo"])

def create_track_from_row(row, user_id):
    return Track(
        title=row["track_name"],
        artist=row["artist"],
        genre=row["genre"],
        tempo=row["tempo"],
        valence=row.get("valence", 0.5),
        energy=row.get("energy", 0.5),
        acousticness=row.get("acousticness", 0.3),
        danceability=row.get("danceability", 0.7),
        liveness=row.get("liveness", 0.1),
        mode="Major" if row.get("mode", 1) == 1 else "Minor",
        duration_ms=int(row.get("duration_ms", 200000)),
        user_id=user_id
    )

def link_usertrack(user, track):
    return UserTrack(
        user_id=user.id,
        track_id=track.id,
        song=track.title,
        artist=track.artist,
        song_duration=track.duration_ms,
        times_played=1,
        total_ms_listened=track.duration_ms
    )

def seed_users():
    user_data = [
        {"username": "vmontes", "email": "hallen@hotmail.com"},
        {"username": "steven12", "email": "hammondjacob@yahoo.com"},
        {"username": "cmartinez", "email": "gellis@clark.com"},
        {"username": "raymond89", "email": "chase26@castillo.org"},
        {"username": "vmiller", "email": "ivanchen@gmail.com"},
        {"username": "cruzdenise", "email": "wscott@johnson.com"},
        {"username": "pagetamara", "email": "jeffreysmith@hotmail.com"},
        {"username": "connie96", "email": "nathanmay@yahoo.com"},
        {"username": "hobbsmatthew", "email": "lauralove@gmail.com"},
    ]

    created_users = []
    for u in user_data:
        user = User(
            username=u["username"],
            email=u["email"],
            password_hash=generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.flush()

        for j in range(2):
            playlist = Playlist(name=f"{user.username.title()} Playlist {j+1}", owner_id=user.id)
            db.session.add(playlist)
            db.session.flush()

            track_rows = spotify_df.sample(n=8)
            for _, row in track_rows.iterrows():
                track = create_track_from_row(row, user.id)
                db.session.add(track)
                db.session.flush()
                db.session.add(PlaylistTrack(playlist_id=playlist.id, track_id=track.id))
                db.session.add(link_usertrack(user, track))

        created_users.append(user)

    db.session.commit()
    print(f"✅ Seeded {len(created_users)} users with playlists and tracks.")
    return created_users

def seed_marker_account(users):
    marker = User.query.filter_by(username="marker123").first()
    if not marker:
        marker = User(
            username="marker123",
            email="marker@example.com",
            name="Marker User",
            password_hash=generate_password_hash("testmarker"),
            dob=datetime(1990, 1, 1),
            gender="Other",
            mobile="0000000000",
            profile_pic="default_profile.jpg"
        )
        db.session.add(marker)
        db.session.commit()

    mellow_rows = spotify_df[spotify_df["valence"] < 0.4].sample(n=8)
    hype_rows = spotify_df[spotify_df["energy"] > 0.7].sample(n=8)

    playlist1 = Playlist(name="Marker's Mood Mix", owner_id=marker.id)
    playlist2 = Playlist(name="Marker's Energy Set", owner_id=marker.id)
    db.session.add_all([playlist1, playlist2])
    db.session.commit()

    for row in mellow_rows.itertuples():
        t = create_track_from_row(row._asdict(), marker.id)
        db.session.add(t)
        db.session.flush()
        db.session.add(PlaylistTrack(playlist_id=playlist1.id, track_id=t.id))
        db.session.add(link_usertrack(marker, t))

    for row in hype_rows.itertuples():
        t = create_track_from_row(row._asdict(), marker.id)
        db.session.add(t)
        db.session.flush()
        db.session.add(PlaylistTrack(playlist_id=playlist2.id, track_id=t.id))
        db.session.add(link_usertrack(marker, t))

    db.session.commit()

    for user in users:
        if user.username in ["vmontes", "steven12", "cmartinez", "raymond89"]:
                    db.session.add(Friend(user_id=user.id, friend_id=marker.id, is_accepted=True))

        # Create and share two playlists for this friend
        for i in range(2):
            playlist = Playlist(name=f"{user.username.title()}'s Shared Playlist {i+1}", owner_id=user.id)
            db.session.add(playlist)
            db.session.flush()

            # Select 8 real tracks with full data
            sample_tracks = spotify_df.dropna(subset=[
                "track_name", "artist", "album_name", "genre", "danceability",
                "energy", "liveness", "acousticness", "valence", "mode", "tempo", "duration_ms"
            ]).sample(n=8)

            for _, row in sample_tracks.iterrows():
                track = Track(
                    title=row["track_name"],
                    artist=row["artist"],
                    genre=row["genre"],
                    tempo=row["tempo"],
                    valence=row["valence"],
                    energy=row["energy"],
                    acousticness=row["acousticness"],
                    danceability=row["danceability"],
                    liveness=row["liveness"],
                    mode="Major" if row["mode"] == 1 else "Minor",
                    duration_ms=int(row["duration_ms"]),
                    user_id=user.id
                )
                db.session.add(track)
                db.session.flush()

                db.session.add(PlaylistTrack(playlist_id=playlist.id, track_id=track.id))
                db.session.add(link_usertrack(user, track))

            # Share with marker
            share = Share(
                playlist_id=playlist.id,
                recipient_id=marker.id,
                owner_id=user.id
            )
            db.session.add(share)

        if user.username in ["vmiller", "cruzdenise", "pagetamara", "connie96"]:
            db.session.add(Friend(user_id=user.id, friend_id=marker.id, is_accepted=False))
        elif user.username == "hobbsmatthew":
            db.session.add(Friend(user_id=marker.id, friend_id=user.id, is_accepted=False))

    db.session.commit()
    print("✅ Marker seeded with playlists, shared data, and friends.")

def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        users = seed_users()
        seed_marker_account(users)
        print("🎉 All data seeded and ready.")

if __name__ == "__main__":
    main()
