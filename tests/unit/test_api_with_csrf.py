# tests/unit/test_api_with_csrf.py

import pytest
from app import create_app, db
from app.models import User, Playlist
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

def test_api_with_csrf(client):
    user = User.query.filter_by(username='alice').first()
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
    resp = client.post(
        '/api/playlist/1',
        json={'name': 'Updated Name'}
    )
    assert resp.status_code == 200
    updated = Playlist.query.get(1)
    assert updated.name == 'Updated Name'
