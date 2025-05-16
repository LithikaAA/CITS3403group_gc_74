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
    """Test a simplified playlist creation flow."""
    DEFAULT_TIMEOUT = 10
    
    # Step 1: Login
    browser.get(f"{live_server_url}/auth/login")
    
    # Find and fill username field
    username_field = find_element_with_multiple_selectors(
        browser, ["#username", "#email", "[name='identifier']", "[name='email']", "[name='username']"]
    )
    username_field.send_keys("test@example.com")
    
    # Find and fill password field
    password_field = find_element_with_multiple_selectors(browser, ["#password", "[name='password']"])
    password_field.send_keys("password123")
    
    # Find and click login button
    login_button = find_element_with_multiple_selectors(
        browser, ["button[type='submit']", "input[type='submit']", ".btn-login", "#login-button"]
    )
    login_button.click()
    
    # Wait for redirect away from login page
    WebDriverWait(browser, DEFAULT_TIMEOUT).until(
        lambda driver: "/auth/login" not in driver.current_url
    )
    
    # Step 2: Find and navigate to playlist creation
    # Try multiple potential routes based on your route list
    for route in ['/dashboard/playlist/create', '/upload', '/upload/create-playlist']:
        try:
            browser.get(f"{live_server_url}{route}")
            take_screenshot(browser, f"creation_page_{route.replace('/', '_')}")
            
            # Look for playlist name field
            try:
                playlist_name_field = find_element_with_multiple_selectors(
                    browser, ["#playlist-name", "[name='playlist_name']", "#name"], timeout=3
                )
                # Found the field, break the loop
                break
            except NoSuchElementException:
                continue
                
        except Exception:
            continue
    
    # Set playlist name
    playlist_name_field.clear()
    playlist_name_field.send_keys("Simple Test Playlist")
    
    # Try to find track field (if it exists on this page)
    try:
        track_title_field = find_element_with_multiple_selectors(
            browser, ["#track-title", "[name='track_title']", "#title"], timeout=2
        )
        track_title_field.send_keys("Test Track")
        
        track_artist_field = find_element_with_multiple_selectors(
            browser, ["#track-artist", "[name='track_artist']", "#artist"], timeout=2
        )
        track_artist_field.send_keys("Test Artist")
        
        # Try to find add track button
        try:
            add_track_button = find_element_with_multiple_selectors(
                browser, ["#add-track-btn", ".add-track", "//button[contains(text(), 'Add Track')]"], timeout=2
            )
            add_track_button.click()
        except NoSuchElementException:
            # Maybe there's no add track button, that's okay
            pass
    except NoSuchElementException:
        # No track fields, that's okay too - might be a two-step process
        pass
    
    # Find create playlist button
    create_button = find_element_with_multiple_selectors(
        browser, ["#create-playlist-btn", ".create-playlist", "//button[contains(text(), 'Create')]",
                 "//input[@value='Create']", "[type='submit']"]
    )
    create_button.click()
    
    # Step 3: Wait for confirmation (toast, redirect, or some indication of success)
    take_screenshot(browser, "after_playlist_creation")
    
    # Check for success message or redirect
    toast_text = wait_for_toast_or_success(browser)
    
    if toast_text:
        print(f"✅ Received confirmation: {toast_text}")
    else:
        # No toast found, check if we were redirected away from creation page
        WebDriverWait(browser, DEFAULT_TIMEOUT).until(
            lambda driver: "/create" not in driver.current_url or "/upload" not in driver.current_url
        )
        print("✅ Redirected after playlist creation")
    
    # Step 4: Verify playlist exists on dashboard
    browser.get(f"{live_server_url}/dashboard/")
    take_screenshot(browser, "dashboard_after_creation")
    
    # Look for the created playlist in the page content
    page_content = WebDriverWait(browser, DEFAULT_TIMEOUT).until(
        lambda d: d.page_source
    )
    assert "Simple Test Playlist" in page_content, "Created playlist not found on dashboard"
    print("✅ Playlist appears on dashboard")

def test_simple_friend_request(browser, live_server_url):
    """Test a simplified friend request flow."""
    DEFAULT_TIMEOUT = 10
    
    # Setup - create users if needed
    app = create_app()
    with app.app_context():
        # Create main test user if doesn't exist
        if not User.query.filter_by(email="test@example.com").first():
            main_user = User(username="testuser", email="test@example.com")
            main_user.set_password("password123")
            db.session.add(main_user)
        
        # Create friend user if doesn't exist
        friend = User.query.filter_by(username="frienduser").first()
        if not friend:
            friend = User(username="frienduser", email="friend@example.com")
            friend.set_password("password123")
            db.session.add(friend)
        
        db.session.commit()
    
    # Step 1: Login
    browser.get(f"{live_server_url}/auth/login")
    
    username_field = find_element_with_multiple_selectors(
        browser, ["#username", "#email", "[name='identifier']", "[name='email']", "[name='username']"]
    )
    username_field.send_keys("test@example.com")
    
    password_field = find_element_with_multiple_selectors(browser, ["#password", "[name='password']"])
    password_field.send_keys("password123")
    
    login_button = find_element_with_multiple_selectors(
        browser, ["button[type='submit']", "input[type='submit']", ".btn-login", "#login-button"]
    )
    login_button.click()
    
    # Step 2: Find and navigate to add friend page
    # Try different potential friend pages based on your routes
    for route in ['/add-friend', '/friends/add', '/friends/list', '/friends']:
        try:
            browser.get(f"{live_server_url}{route}")
            take_screenshot(browser, f"friends_page_{route.replace('/', '_')}")
            
            # Look for username field
            try:
                username_field = find_element_with_multiple_selectors(
                    browser, ["#friend-username", "[name='username']", "#username", "[name='friend']"], timeout=3
                )
                # Found the field, break the loop
                break
            except NoSuchElementException:
                continue
        except Exception:
            continue
    
    # Fill in friend's username
    username_field.clear()
    username_field.send_keys("frienduser")
    
    # Find and click add friend button
    add_btn = find_element_with_multiple_selectors(
        browser, ["#add-friend-btn", ".add-friend", "//button[contains(text(), 'Add Friend')]",
                 "//input[@value='Add Friend']", "[type='submit']"]
    )
    add_btn.click()
    take_screenshot(browser, "after_friend_request")
    
    # Check for success message or redirect
    toast_text = wait_for_toast_or_success(browser)
    
    if toast_text:
        assert any(x in toast_text.lower() for x in ["request sent", "added", "success"]), f"Unexpected toast: {toast_text}"
        print(f"✅ Friend request confirmation: {toast_text}")
    else:
        # Check if we were redirected
        time.sleep(1)  # Small wait to ensure redirect completed
        print(f"Current URL after friend request: {browser.current_url}")
        print("✅ Friend request submitted")
    
    # Step 3: Verify friend request in database
    with app.app_context():
        main_user = User.query.filter_by(email="test@example.com").first()
        friend_user = User.query.filter_by(username="frienduser").first()
        
        # Check if friend request exists
        request = Friend.query.filter_by(
            user_id=main_user.id, 
            friend_id=friend_user.id
        ).first()
        
        assert request is not None, "Friend request not found in database"
        print("✅ Friend request recorded in database")