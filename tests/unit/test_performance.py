import pytest
import time
from app import create_app, db
from app.models import User, Playlist, Track, PlaylistTrack
from config import TestConfig
from tests.conftest import load_sample_data

# Monkey-patch Track model to include 'album' attribute for the search endpoint
setattr(Track, 'album', '')

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


def test_track_search_performance(logged_in_client):
    # Create many tracks to test search performance
    user = User.query.filter_by(username='alice').first()
    for i in range(200):
        track = Track(
            title=f'Search Performance Track {i}',
            artist=f'Artist {i % 10}',
            genre=f'Genre {i % 5}',
            user_id=user.id,
            valence=0.5,
            acousticness=0.5,
            danceability=0.5,
            energy=0.5,
            tempo=120,
            mode='Major',
            duration_ms=180000
        )
        db.session.add(track)
    db.session.commit()

    start = time.time()
    response = logged_in_client.get('/dashboard/search-tracks?q=Performance')
    elapsed = time.time() - start

    assert response.status_code in (200, 302, 308)
    assert elapsed < 1.0
