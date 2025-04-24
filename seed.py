from app import create_app, db
from app.models import User, Track, SharedVisualisation
from datetime import datetime

app = create_app()

with app.app_context():
    # Clear and recreate tables if needed
    db.drop_all()
    db.create_all()

    # Create two users
    user1 = User(username="alice", email="alice@example.com", password_hash="fakehash1")
    user2 = User(username="bob", email="bob@example.com", password_hash="fakehash2")

    db.session.add_all([user1, user2])
    db.session.commit()

    # Create tracks for user1
    track1 = Track(name="Track A1", artist="Artist X", genre="Pop", valence=0.7,
                   energy=0.6, tempo=120, date_played=datetime.now(UTC), user_id=user1.id)
    track2 = Track(name="Track A2", artist="Artist Y", genre="Rock", valence=0.5,
                   energy=0.8, tempo=140, date_played=datetime.now(UTC), user_id=user1.id)

    # Create tracks for user2
    track3 = Track(name="Track B1", artist="Artist Z", genre="Jazz", valence=0.9,
                   energy=0.4, tempo=100, date_played=datetime.now(UTC), user_id=user2.id)
    track4 = Track(name="Track B2", artist="Artist W", genre="EDM", valence=0.6,
                   energy=0.9, tempo=130, date_played=datetime.now(UTC), user_id=user2.id)

    db.session.add_all([track1, track2, track3, track4])
    db.session.commit()

    # Share a visualisation from Alice to Bob
    shared = SharedVisualisation(
        shared_by_id=user1.id,
        shared_with_id=user2.id,
        chart_type="bar",  # just an example type
        timestamp=datetime.utcnow()
    )

    db.session.add(shared)
    db.session.commit()

    print("Seeded users, tracks, and a shared visualisation.")
