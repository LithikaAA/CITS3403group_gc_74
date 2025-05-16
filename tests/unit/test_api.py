# tests/unit/test_api.py

import pytest
from app import create_app, db
from app.models import User, Playlist, Track, PlaylistTrack
from config import TestConfig
from tests.conftest import load_sample_data

@pytest.fixture(scope="function")
def app():
    app = create_app(config_class=TestConfig)
    ctx = app.app_context()
    ctx.push()
    db.create_all()
    load_sample_data()
    yield app
    db.session.remove()
    db.drop_all()
    ctx.pop()

@pytest.fixture(scope="function")
def client(app):
    return app.test_client()

@pytest.fixture(scope="function")
def logged_in_client(app, client):
    user = User.query.filter_by(username='alice').first()
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
    return client

def test_create_playlist_api(logged_in_client):
    user = User.query.filter_by(username='alice').first()
    payload = {
        "playlist_name": "New Test Playlist",
        "tracks": [
            {
                "title": "New Track 1",
                "artist": "Test Artist",
                "genre": "Test Genre",
                "valence": 0.8,
                "acousticness": 0.3,
                "danceability": 0.7,
                "energy": 0.6,
                "tempo": 110,
                "mode": "Major",
                "duration_ms": 210000
            }
        ]
    }
    response = logged_in_client.post('/upload/create-playlist', json=payload)
    assert response.status_code == 200

    playlist = Playlist.query.filter_by(name="New Test Playlist").first()
    assert playlist is not None
    assert playlist.owner_id == user.id

    track = Track.query.filter_by(title="New Track 1").first()
    assert track is not None
    pt = PlaylistTrack.query.filter_by(playlist_id=playlist.id, track_id=track.id).first()
    assert pt is not None

def test_get_playlist_details(logged_in_client):
    playlist = Playlist.query.filter_by(name='Alice Hits').first()
    response = logged_in_client.get(f'/api/playlist/{playlist.id}')
    assert response.status_code == 200
    assert b'Alice Hits' in response.data

def test_edit_playlist_name(logged_in_client):
    playlist = Playlist.query.filter_by(name='Alice Hits').first()
    response = logged_in_client.post(
        f'/api/playlist/{playlist.id}',
        json={'name': 'Updated Alice Playlist'},
        follow_redirects=True
    )
    assert response.status_code == 200
    updated = Playlist.query.get(playlist.id)
    assert updated.name == 'Updated Alice Playlist'

def test_delete_playlist(logged_in_client):
    playlist = Playlist.query.filter_by(name='Alice Hits').first()
    pid = playlist.id
    response = logged_in_client.delete(f'/api/playlist/{pid}', follow_redirects=True)
    assert response.status_code == 200
    assert Playlist.query.get(pid) is None

def test_add_track_to_playlist(logged_in_client):
    playlist = Playlist.query.filter_by(name='Alice Hits').first()
    track = Track.query.filter_by(title='Track B').first()
    response = logged_in_client.post(
        f'/api/playlist/{playlist.id}/add-track',
        json={'track_id': track.id}
    )
    assert response.status_code == 200
    pt = PlaylistTrack.query.filter_by(playlist_id=playlist.id, track_id=track.id).first()
    assert pt is not None

def test_remove_track_from_playlist(logged_in_client):
    playlist = Playlist.query.filter_by(name='Alice Hits').first()
    track = Track.query.filter_by(title='Track A').first()
    pt = PlaylistTrack(playlist_id=playlist.id, track_id=track.id)
    db.session.add(pt)
    db.session.commit()
    response = logged_in_client.delete(
        f'/api/playlist/{playlist.id}/remove-track/{track.id}',
        follow_redirects=True
    )
    assert response.status_code == 200
    assert PlaylistTrack.query.filter_by(playlist_id=playlist.id, track_id=track.id).first() is None

def test_share_playlist(logged_in_client):
    playlist = Playlist.query.filter_by(name='Alice Hits').first()
    response = logged_in_client.post(
        '/share/',
        data={'playlist_id': playlist.id, 'friend_username': 'bob'},
        follow_redirects=True
    )
    assert response.status_code == 200
