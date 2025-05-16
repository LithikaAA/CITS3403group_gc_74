import pytest
import os
from selenium.webdriver.common.by import By
from app import create_app, db
from app.models import User, Playlist

@pytest.fixture(autouse=True)
def setup_user():
    """Create test user."""
    app = create_app()
    with app.app_context():
        if not User.query.filter_by(email="test@example.com").first():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()

def login(browser, live_server_url):
    """Simple login function."""
    browser.get(f"{live_server_url}/auth/login")
    browser.execute_script("""
        // Fill first non-hidden input with email
        document.querySelector('input:not([type="hidden"])').value = 'test@example.com';
        // Fill first password input
        document.querySelector('input[type="password"]').value = 'password123';
        // Submit the form
        document.querySelector('form').submit();
    """)
    browser.implicitly_wait(3)

def test_playlist_exists(browser, live_server_url):
    """Verify playlist creation at the database level."""
    # Login
    login(browser, live_server_url)
    
    # Create a playlist directly in the database
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        
        # Delete any existing test playlists first
        Playlist.query.filter_by(name="Test Playlist").delete()
        db.session.commit()
        
        # Create a new test playlist
        playlist = Playlist(name="Test Playlist", owner_id=user.id)
        db.session.add(playlist)
        db.session.commit()
    
    # Navigate to dashboard
    browser.get(f"{live_server_url}/dashboard/")
    browser.save_screenshot("screenshots/dashboard.png")
    
    # Verify playlist exists in page source
    assert "Test Playlist" in browser.page_source