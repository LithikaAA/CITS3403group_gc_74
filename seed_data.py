from faker import Faker
from app import create_app
from app.models import db, User, Track, Friend
import random

app = create_app()
fake = Faker()

with app.app_context():
    # Clear existing data
    Friend.query.delete()
    Track.query.delete()
    User.query.delete()
    db.session.commit()

    # Create users
    users = []
    for _ in range(10):
        user = User(
            username=fake.user_name(),
            email=fake.email(),
            name=fake.name(),
            gender=random.choice(["Male", "Female", "Other"]),
            mobile=fake.phone_number(),
            profile_pic="avatar.png"
        )
        user.set_password("test123")
        db.session.add(user)
        users.append(user)

    db.session.commit()

    # Add tracks for each user
    for user in users:
        for _ in range(random.randint(5, 15)):
            track = Track(
                title=fake.word(),
                artist=fake.name(),
                genre=random.choice(["Pop", "Rock", "Jazz", "Hip-Hop", "Electronic"]),
                tempo=random.uniform(60, 180),
                valence=random.random(),
                energy=random.random(),
                user_id=user.id
            )
            db.session.add(track)

    # Add friends randomly
    for user in users:
        others = [u for u in users if u.id != user.id]
        friends = random.sample(others, k=3)
        for friend in friends:
            db.session.add(Friend(user_id=user.id, friend_id=friend.id))

    db.session.commit()
    print("✅ Seed complete!")
