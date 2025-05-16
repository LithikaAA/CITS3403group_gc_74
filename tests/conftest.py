import pytest
import os
import socket
import sys
import time
import threading
import subprocess
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app import create_app, db
from app.models import User, Playlist, Track, PlaylistTrack, Friend


def wait_for_port(host, port, timeout=10):
    """Wait for a port to be open on a host."""
    print(f"Waiting for server on {host}:{port}...")
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            with socket.create_connection((host, port), timeout=1):
                print(f"Server is up on {host}:{port}")
                return True
        except OSError:
            time.sleep(0.5)
    raise RuntimeError(
        f"Server on {host}:{port} not responding within {timeout} seconds."
    )


def load_sample_data():
    """Load sample data for testing."""
    # Create users
    alice = User(username='alice', email='alice@example.com')
    alice.set_password('password')
    bob = User(username='bob', email='bob@example.com')
    bob.set_password('password')
    
    db.session.add_all([alice, bob])
    db.session.flush()
    
    # Create playlists
    alice_playlist = Playlist(name='Alice Hits', owner_id=alice.id)
    bob_playlist = Playlist(name='Bob Vibes', owner_id=bob.id)
    
    db.session.add_all([alice_playlist, bob_playlist])
    db.session.flush()
    
    # Create tracks
    tracks = [
        Track(
            title='Track A', 
            artist='Artist X', 
            genre='Pop', 
            user_id=alice.id,
            valence=0.7, 
            acousticness=0.2, 
            danceability=0.9, 
            energy=0.8, 
            tempo=120, 
            mode="Major", 
            duration_ms=180000
        ),
        Track(
            title='Track B', 
            artist='Artist Y', 
            genre='Rock', 
            user_id=alice.id,
            valence=0.4, 
            acousticness=0.6, 
            danceability=0.5, 
            energy=0.5, 
            tempo=95, 
            mode="Minor", 
            duration_ms=150000
        ),
        Track(
            title='Track C', 
            artist='Artist Z', 
            genre='EDM', 
            user_id=bob.id,
            valence=0.9, 
            acousticness=0.1, 
            danceability=0.8, 
            energy=0.9, 
            tempo=130, 
            mode="Major", 
            duration_ms=240000
        ),
    ]
    
    db.session.add_all(tracks)
    db.session.commit()


def load_fixed_test_data():
    """Load data specifically for the fixed tests with unique identifiers."""
    # Check if the fixed test user already exists
    fixed_user = User.query.filter_by(email="fixed_test@example.com").first()
    if fixed_user:
        return  # Data already loaded
    
    # Create fixed test users
    fixed_user = User(username='fixed_testuser', email='fixed_test@example.com')
    fixed_user.set_password('password123')
    fixed_friend = User(username='fixed_frienduser', email='fixed_friend@example.com')
    fixed_friend.set_password('password123')
    
    db.session.add_all([fixed_user, fixed_friend])
    db.session.flush()
    
    # Create friendship
    friendship1 = Friend(user_id=fixed_user.id, friend_id=fixed_friend.id, is_accepted=True)
    friendship2 = Friend(user_id=fixed_friend.id, friend_id=fixed_user.id, is_accepted=True)
    db.session.add_all([friendship1, friendship2])
    
    # Create a test playlist
    fixed_playlist = Playlist(name="Fixed Test Playlist", owner_id=fixed_user.id)
    db.session.add(fixed_playlist)
    db.session.flush()
    
    # Create tracks for fixed tests
    fixed_tracks = [
        Track(
            title='Fixed Track A', 
            artist='Fixed Artist X', 
            genre='Pop', 
            user_id=fixed_user.id,
            valence=0.7, 
            acousticness=0.2, 
            danceability=0.9, 
            energy=0.8, 
            tempo=120, 
            mode="Major", 
            duration_ms=180000
        ),
        Track(
            title='Fixed Track B', 
            artist='Fixed Artist Y', 
            genre='Rock', 
            user_id=fixed_user.id,
            valence=0.4, 
            acousticness=0.6, 
            danceability=0.5, 
            energy=0.5, 
            tempo=95, 
            mode="Minor", 
            duration_ms=150000
        )
    ]
    
    db.session.add_all(fixed_tracks)
    db.session.flush()
    
    # Link a track to the playlist
    playlist_track = PlaylistTrack(
        playlist_id=fixed_playlist.id, 
        track_id=fixed_tracks[0].id
    )
    db.session.add(playlist_track)
    
    db.session.commit()


# Selenium helper function
def find_element_with_multiple_selectors(browser, selectors, timeout=5):
    """Try multiple selectors to find an element, return the first one that works."""
    for selector in selectors:
        try:
            if selector.startswith("//"):
                # XPath selector
                return WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            else:
                # CSS selector
                return WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
        except (TimeoutException, NoSuchElementException):
            continue
    
    # If we get here, none of the selectors worked
    raise NoSuchElementException(f"Could not find element with any of these selectors: {selectors}")


def take_screenshot(browser, name):
    """Take a screenshot for debugging purposes."""
    os.makedirs("selenium_screenshots", exist_ok=True)
    filename = f"selenium_screenshots/{name}_{int(time.time())}.png"
    browser.save_screenshot(filename)
    print(f"Screenshot saved: {filename}")


def wait_for_toast_or_success(browser, timeout=10):
    """Wait for a toast message or other success indicator."""
    for selector in [
        ".toast-message", ".alert-success", ".notification", 
        "#success-message", ".toast", "[role='alert']"
    ]:
        try:
            element = WebDriverWait(browser, timeout/len([".toast-message", ".alert-success", 
                                                         ".notification", "#success-message", 
                                                         ".toast", "[role='alert']"])).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.text
        except (TimeoutException, NoSuchElementException):
            continue
    
    # Return empty string if no toast found
    return ""


@pytest.fixture(scope="module")
def browser():
    """Provide a selenium webdriver instance with Chrome."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")  
    
    # Try with just the options
    driver = webdriver.Chrome(options=options)
    
    yield driver
    driver.quit()


@pytest.fixture(scope="module", autouse=True)
def app_server():
    """Set up and tear down a live Flask server for testing."""
    env = os.environ.copy()
    env["FLASK_APP"] = "run.py"
    env["FLASK_ENV"] = "testing"
    python_executable = sys.executable
    
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        load_sample_data()
        load_fixed_test_data()  # Load additional fixed test data
        
        # Create test user for selenium tests
        test_user = User.query.filter_by(email="test@example.com").first()
        if not test_user:
            test_user = User(username="testuser", email="test@example.com")
            test_user.set_password("password123")
            db.session.add(test_user)
            db.session.commit()
    
    # Create the port file directly with a fixed port
    port = 5000
    with open(".flask-test-port", "w") as f:
        f.write(str(port))
    
    server = subprocess.Popen(
        [python_executable, "run.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        env=env,
        text=True,
    )
    
    def print_server_logs(proc):
        for line in proc.stdout:
            print("Flask:", line.strip())
    
    threading.Thread(target=print_server_logs, args=(server,), daemon=True).start()
    
    # Wait a bit for the server to start
    time.sleep(2)
    
    try:
        wait_for_port("localhost", port)
        print(f"Flask server is ready on port {port}")
        yield
    finally:
        with app.app_context():
            db.drop_all()
        server.terminate()
        server.wait()
        if os.path.exists(".flask-test-port"):
            os.remove(".flask-test-port")


@pytest.fixture(scope="module")
def live_server_url():
    """Get the URL of the live server."""
    return "http://localhost:5000"


@pytest.fixture(scope="function")
def app():
    """Create a Flask application for testing."""
    app = create_app()
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    load_sample_data()
    load_fixed_test_data()  # Load data for fixed tests too
    yield app
    db.session.remove()
    db.drop_all()
    app_context.pop()


@pytest.fixture(scope="function")
def client(app):
    """Create a test client for the Flask application."""
    return app.test_client()


@pytest.fixture(scope="function")
def setup_test_user():
    """Create a test user for each test function."""
    app = create_app()
    with app.app_context():
        user = User.query.filter_by(email="test@example.com").first()
        if not user:
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
    yield
    # No teardown needed, will be handled by module-level fixture


@pytest.fixture(scope="function")
def auth_client(app, client):
    """Create an authenticated test client."""
    with app.app_context():
        # Use the fixed test user for fixed tests
        user = User.query.filter_by(email="fixed_test@example.com").first()
        assert user is not None, "Fixed test user not found. Was load_fixed_test_data() called?"
    
    with client.session_transaction() as sess:
        sess['_user_id'] = str(user.id)
    
    return client


@pytest.fixture(scope="function")
def fixed_user(app):
    """Get the fixed test user for fixed tests."""
    with app.app_context():
        user = User.query.filter_by(email="fixed_test@example.com").first()
        assert user is not None, "Fixed test user not found. Was load_fixed_test_data() called?"
        return user


@pytest.fixture(scope="function")
def fixed_friend(app):
    """Get the fixed friend user for fixed tests."""
    with app.app_context():
        user = User.query.filter_by(email="fixed_friend@example.com").first()
        assert user is not None, "Fixed friend user not found. Was load_fixed_test_data() called?"
        return user


@pytest.fixture(scope="function")
def fixed_playlist(app, fixed_user):
    """Get the fixed test playlist for fixed tests."""
    with app.app_context():
        playlist = Playlist.query.filter_by(
            name="Fixed Test Playlist", 
            owner_id=fixed_user.id
        ).first()
        assert playlist is not None, "Fixed test playlist not found. Was load_fixed_test_data() called?"
        return playlist