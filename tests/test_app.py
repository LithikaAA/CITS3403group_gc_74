import unittest
from app import create_app, db
from app.models import User, Playlist, Track, Friend, PlaylistTrack
from werkzeug.security import generate_password_hash
from flask import url_for
from flask_login import login_user
from config import TestConfig
import os
print("Current working directory:", os.getcwd())

def load_sample_data():
    user1 = User(username='alice', email='alice@example.com', password_hash=generate_password_hash('password'))
    user2 = User(username='bob', email='bob@example.com', password_hash=generate_password_hash('password'))

    db.session.add_all([user1, user2])
    db.session.flush()  # get user1.id and user2.id

    playlist1 = Playlist(name='Alice Hits', owner_id=user1.id)
    playlist2 = Playlist(name='Bob Vibes', owner_id=user2.id)
    db.session.add_all([playlist1, playlist2])
    db.session.flush()

    tracks = [
        Track(title='Track A', artist='Artist X', genre='Pop', user_id=user1.id,
              valence=0.7, acousticness=0.2, danceability=0.9, energy=0.8, tempo=120, mode="Major", duration_ms=180000),
        Track(title='Track B', artist='Artist Y', genre='Rock', user_id=user1.id,
              valence=0.4, acousticness=0.6, danceability=0.5, energy=0.5, tempo=95, mode="Minor", duration_ms=150000),
        Track(title='Track C', artist='Artist Z', genre='EDM', user_id=user2.id,
              valence=0.9, acousticness=0.1, danceability=0.8, energy=0.9, tempo=130, mode="Major", duration_ms=240000),
    ]

    db.session.add_all(tracks)
    db.session.commit()

class FlaskAppTestCase(unittest.TestCase):
    
    def setUp(self):
        self.maxDiff = None
        self.app = create_app(config_class=TestConfig)
        with self.app.app_context():
            db.drop_all()
            db.create_all()
            load_sample_data()
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_intro_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_dashboard_page(self):
        with self.app.app_context():
            user = User.query.filter_by(username='alice').first()
            user_id = user.id
            
        with self.client.session_transaction() as session:
            session['_user_id'] = str(user_id)

        response = self.client.get('/dashboard/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)


    def test_upload_page(self):
        with self.app.app_context():
            user = User.query.filter_by(username='alice').first()
            user_id = user.id
        with self.client.session_transaction() as session:
            session['_user_id'] = str(user_id)
        response = self.client.get('/upload', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upload', response.data)

    def test_share_page(self):
        with self.app.app_context():
            user = User.query.filter_by(username='alice').first()
            user_id = user.id
        with self.client.session_transaction() as session:
            session['_user_id'] = str(user_id) 
        response = self.client.get('/share/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Share', response.data)

    def test_login_page(self):
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)

    def test_signup_page(self):
        response = self.client.get('/auth/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)

    def test_signup_and_login(self):
        # Signup
        response = self.client.post('/auth/signup', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Login', response.data)

        # Login
        response = self.client.post('/auth/login', data={
            'username_or_email': 'test@example.com',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertIn(b'Dashboard', response.data)

    def test_add_friend_success(self):
        with self.app.app_context():
            user1 = User(username='user1', email='user1@example.com')
            user1.set_password('testpass')
            user2 = User(username='user2', email='user2@example.com')
            user2.set_password('testpass')
            db.session.add_all([user1, user2])
            db.session.flush()
            user1_id = user1.id
            user2_id = user2.id
            db.session.commit()

        with self.client.session_transaction() as session:
            session['_user_id'] = str(user1_id)

        response = self.client.post(
            '/add-friend',
            data={'friend_username': 'user2'},
            follow_redirects=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Friend request sent to user2!', response.data)

        with self.app.app_context():
            friendship = Friend.query.filter_by(user_id=user1_id, friend_id=user2_id).first()
            self.assertIsNotNone(friendship)

    def test_invalid_login(self):
        response = self.client.post('/auth/login', data={
            'identifier': 'wronguser',
            'password': 'wrongpass'
        }, follow_redirects=True)
        self.assertIn(b'Invalid username/email or password.', response.data)

    def test_duplicate_signup(self):
        # Existing user
        self.client.post('/auth/signup', data={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'password123'
        }, follow_redirects=True)

        response = self.client.post('/auth/signup', data={
            'username': 'alice',
            'email': 'alice@example.com',
            'password': 'anotherpassword'
        }, follow_redirects=True)

        self.assertIn(b'Username or email already exists.', response.data)
    
    def test_upload_requires_login(self):
        response = self.client.get('/upload', follow_redirects=True)
        self.assertIn(b'Login', response.data)  # or "Please log in to access"
        
    def test_accept_friend_request(self):
        with self.app.app_context():
            user1 = User(username='u1', email='u1@example.com')
            user1.set_password('test')
            user2 = User(username='u2', email='u2@example.com')
            user2.set_password('test')
            db.session.add_all([user1, user2])
            db.session.flush()
            request = Friend(user_id=user1.id, friend_id=user2.id, is_accepted=False)
            db.session.add(request)
            db.session.commit()
            user2_id = user2.id
            request_id = request.id

        with self.client.session_transaction() as session:
            session['_user_id'] = str(user2_id)

        response = self.client.post(f'/friends/accept/{request_id}', follow_redirects=True)
        self.assertIn(b'Friend request accepted!', response.data)

        with self.app.app_context():
            self.assertTrue(db.session.get(Friend, request_id).is_accepted)
    
    def test_create_playlist_missing_data(self):
        with self.client.session_transaction() as session:
            session['_user_id'] = '1'  # Assuming user ID 1 exists

        response = self.client.post('/upload/create-playlist', json={}, follow_redirects=True)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b'No data provided', response.data)
    
    def test_logout_clears_session(self):
        with self.client.session_transaction() as session:
            session['_user_id'] = '1'
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertIn(b'You have been logged out.', response.data)
        
    def test_remove_friend(self):
        with self.app.app_context():
            user1 = User(username='test1', email='t1@example.com')
            user1.set_password('pass')
            user2 = User(username='test2', email='t2@example.com')
            user2.set_password('pass')
            db.session.add_all([user1, user2])
            db.session.commit()

            user1_id = user1.id
            user2_id = user2.id
            username2 = user2.username

            db.session.add(Friend(user_id=user1_id, friend_id=user2_id, is_accepted=True))
            db.session.add(Friend(user_id=user2_id, friend_id=user1_id, is_accepted=True))
            db.session.commit()

        with self.client.session_transaction() as session:
            session['_user_id'] = str(user1_id)

        response = self.client.post(f'/friends/remove/{username2}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'success', response.data)

        with self.app.app_context():
            self.assertIsNone(Friend.query.filter_by(user_id=user1_id, friend_id=user2_id).first())
            self.assertIsNone(Friend.query.filter_by(user_id=user2_id, friend_id=user1_id).first())
        
    def test_upload_playlist_invalid_track_format(self):
        with self.app.app_context():
            user = User.query.filter_by(username='alice').first()
        with self.client.session_transaction() as session:
            session['_user_id'] = str(user.id)

        bad_data = {
            "playlist_name": "Invalid Playlist",
            "tracks": [{"title": "", "artist": ""}]  # Invalid format
        }
        res = self.client.post('/upload/create-playlist', json=bad_data)
        self.assertEqual(res.status_code, 200)  # Still returns 200, just skips invalid
        self.assertIn(b'"status":"success"', res.data)

    def test_signup_invalid_email_format(self):
        res = self.client.post('/auth/signup', data={
            'username': 'invaliduser',
            'email': 'not-an-email',
            'password': 'password123'
        }, follow_redirects=True)
        self.assertNotEqual(res.status_code, 500)

    def test_create_playlist_empty_name(self):
        with self.app.app_context():
            user = User.query.filter_by(username='alice').first()
        with self.client.session_transaction() as session:
            session['_user_id'] = str(user.id)

        data = {"playlist_name": "", "tracks": []}
        res = self.client.post('/upload/create-playlist', json=data)
        self.assertIn(b'No tracks provided', res.data)
        
if __name__ == '__main__':
    unittest.main()