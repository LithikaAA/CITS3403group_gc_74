# tests/unit/test_security.py

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

def test_input_validation(client):
    """Test input validation for signup with invalid field values."""
    route = '/auth/signup'

    # Each dict now has all required fields, but with one invalid value
    invalid_cases = [
        # username too short
        {'username': 'a', 'email': 'valid@example.com', 'password': 'ValidPass123'},
        # username too long
        {'username': 'u' * 101, 'email': 'valid@example.com', 'password': 'ValidPass123'},
        # invalid email format
        {'username': 'validuser', 'email': 'notanemail', 'password': 'ValidPass123'},
        # password too short
        {'username': 'validuser', 'email': 'valid@example.com', 'password': '123'}
    ]

    for data in invalid_cases:
        resp = client.post(route, data=data, follow_redirects=True)
        # Expect a non-200 (error) or an error message in the body
        assert resp.status_code != 200 or b'error' in resp.data.lower()
