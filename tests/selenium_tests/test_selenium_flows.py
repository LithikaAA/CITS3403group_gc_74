import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app import create_app, db
from app.models import User, Playlist, Track, Friend, PlaylistTrack, Share

# Create a directory for screenshots if it doesn't exist
os.makedirs("selenium_screenshots", exist_ok=True)

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

def take_screenshot(browser, name):
    """Take a screenshot for debugging purposes."""
    filename = f"selenium_screenshots/{name}_{int(time.time())}.png"
    browser.save_screenshot(filename)
    print(f"Screenshot saved: {filename}")

def test_basic_login_and_navigation(browser, live_server_url):
    """Basic test to verify login and navigation to dashboard."""
    DEFAULT_TIMEOUT = 10
    
    # Setup: Ensure test user exists
    app = create_app()
    with app.app_context():
        # Create test user if it doesn't exist
        if not User.query.filter_by(email="test@example.com").first():
            user = User(username="testuser", email="test@example.com")
            user.set_password("password123")
            db.session.add(user)
            db.session.commit()
    
    # Step 1: Login
    browser.get(f"{live_server_url}/auth/login")
    take_screenshot(browser, "login_page")
    
    # Find username/email field
    username_field = find_element_with_multiple_selectors(
        browser, 
        ["#username", "#email", "[name='identifier']", "[name='email']", "[name='username']"]
    )
    username_field.send_keys("test@example.com")
    
    # Find password field
    password_field = find_element_with_multiple_selectors(
        browser,
        ["#password", "[name='password']"]
    )
    password_field.send_keys("password123")
    
    # Find login button
    login_button = find_element_with_multiple_selectors(
        browser,
        ["button[type='submit']", "input[type='submit']", ".btn-login", 
         "#login-button", "//button[contains(text(), 'Login')]", 
         "//button[contains(text(), 'Sign in')]"]
    )
    login_button.click()
    
    # Step 2: Verify redirect to dashboard
    try:
        # Wait for redirect to dashboard or similar page
        WebDriverWait(browser, DEFAULT_TIMEOUT).until(
            lambda driver: "/auth/login" not in driver.current_url
        )
        take_screenshot(browser, "after_login")
        
        # Check we're on some kind of dashboard/home page
        assert "/login" not in browser.current_url, "Still on login page, login failed"
        print("✅ Login successful")
        
    except TimeoutException:
        take_screenshot(browser, "login_timeout")
        pytest.fail("Timed out waiting for redirect after login")

def test_simple_playlist_creation(browser, live_server_url):
    login(browser, live_server_url)

    for route in ['/dashboard/playlist/create', '/upload', '/upload/create-playlist']:
        browser.get(f"{live_server_url}{route}")
        try:
            playlist_input = WebDriverWait(browser, 5).until(
                EC.presence_of_element_located((By.NAME, "playlist_name"))
            )
            playlist_input.clear()
            playlist_input.send_keys("Simple Test Playlist")
            break
        except:
            continue

    try:
        create_btn = WebDriverWait(browser, 10).until(
            EC.element_to_be_clickable((By.ID, "create-playlist-btn"))
        )
        browser.execute_script("arguments[0].scrollIntoView(true);", create_btn)
        create_btn.click()
    except ElementNotInteractableException:
        pytest.fail("Create playlist button not interactable")

    WebDriverWait(browser, 10).until(lambda d: "Simple Test Playlist" in d.page_source)
    assert "Simple Test Playlist" in browser.page_source


def test_simple_friend_request(browser, live_server_url):
    app = create_app()
    with app.app_context():
        main_user = User.query.filter_by(email="test@example.com").first()
        if not main_user:
            main_user = User(username="testuser", email="test@example.com")
            main_user.set_password("password123")
            db.session.add(main_user)

        friend_user = User.query.filter_by(username="frienduser").first()
        if not friend_user:
            friend_user = User(username="frienduser", email="friend@example.com")
            friend_user.set_password("password123")
            db.session.add(friend_user)

        db.session.commit()
        main_user_id = main_user.id
        friend_user_id = friend_user.id

    login(browser, live_server_url)

    for route in ['/add-friend', '/friends/add', '/friends/list', '/friends']:
        browser.get(f"{live_server_url}{route}")
        try:
            input_field = WebDriverWait(browser, 3).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            input_field.clear()
            input_field.send_keys("frienduser")
            for _ in range(3):
                try:
                    add_btn = WebDriverWait(browser, 5).until(
                        EC.element_to_be_clickable((By.ID, "add-friend-btn"))
                    )
                    browser.execute_script("arguments[0].scrollIntoView(true);", add_btn)
                    add_btn.click()
                    break
                except StaleElementReferenceException:
                    time.sleep(1)
            break
        except:
            continue

    time.sleep(2)
    with app.app_context():
        main_user = db.session.get(User, main_user_id)
        friend_user = db.session.get(User, friend_user_id)
        request = Friend.query.filter_by(user_id=main_user.id, friend_id=friend_user.id).first()
        assert request is not None, "Friend request not found in database"
        print("✅ Friend request recorded")