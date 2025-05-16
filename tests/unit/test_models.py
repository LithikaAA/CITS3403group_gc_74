import pytest
from app import create_app, db
from app.models import User, Playlist, Track, Friend, PlaylistTrack
from werkzeug.security import generate_password_hash
from config import TestConfig
from tests.conftest import load_sample_data

@pytest.fixture(scope="function")
def app():
    app = create_app(config_class=TestConfig)
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    load_sample_data()
    yield app
    db.session.remove()
    db.drop_all()
    app_context.pop()

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

def test_user_playlist_relationship(app):
    """Test user-playlist relationship is properly established."""
    user = User.query.filter_by(username='alice').first()
    playlists = Playlist.query.filter_by(owner_id=user.id).all()
    assert len(playlists) > 0
    assert playlists[0].name == 'Alice Hits'

def test_playlist_track_relationship(app):
    """Test playlist-track relationship through PlaylistTrack model."""
    playlist = Playlist.query.filter_by(name='Alice Hits').first()
    track = Track.query.filter_by(title='Track A').first()
    
    # Add track to playlist - removed position parameter
    pt = PlaylistTrack(playlist_id=playlist.id, track_id=track.id)
    db.session.add(pt)
    db.session.commit()
    
    # Check if track is in playlist
    playlist_tracks = PlaylistTrack.query.filter_by(playlist_id=playlist.id).all()
    assert len(playlist_tracks) > 0
    assert playlist_tracks[0].track_id == track.id

def test_track_attributes(app):
    """Test track music attributes are properly stored and retrieved."""
    track = Track.query.filter_by(title='Track A').first()
    assert track.valence == 0.7
    assert track.acousticness == 0.2
    assert track.danceability == 0.9
    assert track.energy == 0.8
    assert track.tempo == 120
    assert track.mode == "Major"

def test_user_password_hashing(app):
    """Test password hashing and verification."""
    user = User.query.filter_by(username='alice').first()
    assert not user.check_password('incorrect')
    
    # Create a new user with a known password
    user = User(username='passwordtest', email='pwd@example.com')
    user.set_password('securepass')
    db.session.add(user)
    db.session.commit()
    
    # Verify password checking works
    fetched_user = User.query.filter_by(username='passwordtest').first()
    assert fetched_user.check_password('securepass')
    assert not fetched_user.check_password('wrongpass')

def test_friendship_relationship(app):
    """Test that friendship relationships work correctly."""
    alice = User.query.filter_by(username='alice').first()
    bob = User.query.filter_by(username='bob').first()
    
    # Create friendship request
    friendship = Friend(user_id=alice.id, friend_id=bob.id, is_accepted=False)
    db.session.add(friendship)
    db.session.commit()
    
    # Verify request exists
    request = Friend.query.filter_by(user_id=alice.id, friend_id=bob.id).first()
    assert request is not None
    assert request.is_accepted is False
    
    # Accept friendship
    request.is_accepted = True
    db.session.commit()
    
    # Verify friendship is established
    alice_friends = alice.friends_list()
    assert any(friend.id == bob.id for friend in alice_friends)