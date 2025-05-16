# tests/unit/test_edge_case.py

import pytest
import sqlalchemy
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

def test_duplicate_track_in_playlist(logged_in_client):
    playlist = Playlist.query.filter_by(name='Alice Hits').first()
    track = Track.query.filter_by(title='Track A').first()
    pt1 = PlaylistTrack(playlist_id=playlist.id, track_id=track.id)
    db.session.add(pt1)
    db.session.commit()

    pt2 = PlaylistTrack(playlist_id=playlist.id, track_id=track.id)
    db.session.add(pt2)
    with pytest.raises(sqlalchemy.exc.IntegrityError):
        db.session.commit()
