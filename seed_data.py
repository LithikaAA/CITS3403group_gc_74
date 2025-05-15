from app import create_app, db
from app.models import User, Playlist, Track, PlaylistTrack, Friend, Share
from werkzeug.security import generate_password_hash
from datetime import datetime

def seed_users():
    users = [
        {"username": "vmontes", "email": "hallen@hotmail.com"},
        {"username": "steven12", "email": "hammondjacob@yahoo.com"},
        {"username": "cmartinez", "email": "gellis@clark.com"},
        {"username": "raymond89", "email": "chase26@castillo.org"},
        {"username": "vmiller", "email": "ivanchen@gmail.com"},
        {"username": "cruzdenise", "email": "wscott@johnson.com"},
        {"username": "pagetamara", "email": "jeffreysmith@hotmail.com"},
        {"username": "connie96", "email": "nathanmay@yahoo.com"},
        {"username": "ashley91", "email": "jeremybell@mckinney.com"},
        {"username": "hobbsmatthew", "email": "lauralove@gmail.com"},
    ]

    count = 0
    for u in users:
        if not User.query.filter(
            (User.username == u["username"]) | (User.email == u["email"])
        ).first():
            user = User(
                username=u["username"],
                email=u["email"],
                password_hash=generate_password_hash("password123")
            )
            db.session.add(user)
            count += 1

    db.session.commit()
    print(f" Seeded {count} new users (out of {len(users)}).")


def seed_marker_account():
    if User.query.filter_by(username="marker123").first():
        print("Marker account already exists.")
        return
    
     # --- Marker User ---
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

    # --- Marker Playlists with 8 Songs Each ---
    def create_track(title, artist, genre, tempo, user_id):
        return Track(
            title=title, artist=artist, genre=genre,
            tempo=tempo, valence=0.6, energy=0.7,
            acousticness=0.3, danceability=0.8, liveness=0.1,
            mode="Major", duration_ms=200000, user_id=user_id
        )

     # --- Marker Playlists with Tracks ---
    playlist1 = Playlist(name="Marker's Mood Mix", owner_id=marker.id)
    playlist2 = Playlist(name="Marker's Energy Set", owner_id=marker.id)
    db.session.add_all([playlist1, playlist2])
    db.session.commit()

    tracks1 = [create_track(f"Chill Track {i}", f"Artist {i}", "Indie", 100 + i, marker.id) for i in range(8)]
    tracks2 = [create_track(f"Hype Track {i}", f"DJ {i}", "EDM", 120 + i, marker.id) for i in range(8)]
    db.session.add_all(tracks1 + tracks2)
    db.session.commit()

    db.session.add_all([PlaylistTrack(playlist_id=playlist1.id, track_id=track.id) for track in tracks1])
    db.session.add_all([PlaylistTrack(playlist_id=playlist2.id, track_id=track.id) for track in tracks2])
    db.session.commit()

    # --- Friends with Their Own Data ---
    def add_friend_user(username, email):
        u = User(username=username, email=email, password_hash=generate_password_hash("password123"))
        db.session.add(u)
        db.session.commit()
        p = Playlist(name=f"{username}'s Picks", owner_id=u.id)
        db.session.add(p)
        db.session.commit()
        friend_tracks = [create_track(f"{username} Track {i}", f"F-{i}", "Rock", 110 + i, u.id) for i in range(6)]
        db.session.add_all(friend_tracks)
        db.session.commit()
        db.session.add_all([PlaylistTrack(playlist_id=p.id, track_id=t.id) for t in friend_tracks])
        db.session.commit()
        return u, p

    friend_a, _ = add_friend_user("friend_a", "fa@example.com")
    friend_b, friend_b_playlist = add_friend_user("friend_b", "fb@example.com")
    friend_c, _ = add_friend_user("friend_c", "fc@example.com")

    # --- Accepted Friendships ---
    db.session.add_all([
        Friend(user_id=marker.id, friend_id=friend_a.id, is_accepted=True),
        Friend(user_id=friend_a.id, friend_id=marker.id, is_accepted=True),
        Friend(user_id=friend_b.id, friend_id=marker.id, is_accepted=True),
        Friend(user_id=marker.id, friend_id=friend_b.id, is_accepted=True),
    ])

    # --- Incoming Friend Requests ---
    incoming1 = User(username="incoming1", email="in1@example.com", password_hash=generate_password_hash("pass"))
    incoming2 = User(username="incoming2", email="in2@example.com", password_hash=generate_password_hash("pass"))
    db.session.add_all([incoming1, incoming2])
    db.session.commit()

    db.session.add_all([
        Friend(user_id=incoming1.id, friend_id=marker.id, is_accepted=False),
        Friend(user_id=incoming2.id, friend_id=marker.id, is_accepted=False)
    ])

    # --- Outgoing Friend Request from Marker ---
    db.session.add(Friend(user_id=marker.id, friend_id=friend_c.id, is_accepted=False))

    # --- Share Friend B's Playlist with Marker ---
    shared = Share(playlist_id=friend_b_playlist.id, owner_id=friend_b.id, recipient_id=marker.id)
    db.session.add(shared)
    db.session.commit()

    print(" Marker account with playlists, friends, and shared data seeded.")
    print(f" marker@example.com has:")
    print("- 2 playlists with 8 tracks each")
    print("- 2 accepted friends (friend_a, friend_b)")
    print("- 1 outgoing request to friend_c")
    print("- 2 incoming requests from incoming1 and incoming2")
    print("- 1 playlist shared with them from friend_b")


def main():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        seed_users()
        seed_marker_account()
        print(" All data seeded successfully.")


if __name__ == "__main__":
    main()