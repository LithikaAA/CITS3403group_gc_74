import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    StaleElementReferenceException
)
from app import create_app, db
from app.models import User, Playlist, Track, Friend, PlaylistTrack, Share

# Create a directory for screenshots if it doesn't exist
os.makedirs("selenium_screenshots", exist_ok=True)


def find_element_with_multiple_selectors(browser, selectors, timeout=5):
    for selector in selectors:
        try:
            if selector.startswith("//"):
                return WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            else:
                return WebDriverWait(browser, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
        except (TimeoutException, NoSuchElementException):
            continue
    raise NoSuchElementException(f"Could not find element with selectors: {selectors}")


def wait_for_toast_or_success(browser, timeout=10):
    for selector in [
        ".toast-message", ".alert-success", ".notification",
        "#success-message", ".toast", "[role='alert']"
    ]:
        try:
            element = WebDriverWait(browser, timeout/6).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, selector))
            )
            return element.text
        except (TimeoutException, NoSuchElementException):
            continue
    return ""


def take_screenshot(browser, name):
    filename = f"selenium_screenshots/{name}_{int(time.time())}.png"
    browser.save_screenshot(filename)
    print(f"📸 Screenshot saved: {filename}")


def login(browser, live_server_url):
    browser.get(f"{live_server_url}/auth/login")
    username_field = find_element_with_multiple_selectors(
        browser, ["#username", "#email", "[name='email']", "[name='username']", "[name='identifier']"]
    )
    username_field.send_keys("test@example.com")

    password_field = find_element_with_multiple_selectors(
        browser, ["#password", "[name='password']"]
    )
    password_field.send_keys("password123")

    login_button = find_element_with_multiple_selectors(
        browser, [
            "button[type='submit']",
            "input[type='submit']",
            ".btn-login",
            "#login-button",
            "//button[contains(text(), 'Login')]",
            "//button[contains(text(), 'Sign in')]"
        ]
    )
    login_button.click()

    WebDriverWait(browser, 10).until(
        lambda driver: "/auth/login" not in driver.current_url
    )


def test_simple_playlist_creation(browser, live_server_url):
    login(browser, live_server_url)

    browser.get(f"{live_server_url}/upload")

    # Inject mock songs into JS state and DOM
    browser.execute_script("""
        document.getElementById("added-songs").classList.remove("hidden");

        const songList = document.getElementById("song-list");
        songList.innerHTML = `
            <li class="song-item" id="song-track-1">
            <input type="checkbox" checked />
            <span>Song 1</span>
            </li>
            <li class="song-item" id="song-track-2">
            <input type="checkbox" checked />
            <span>Song 2</span>
            </li>
        `;

        window.selectedTracks = [
            { id: "track-1", name: "Song 1", artist: "Artist A" },
            { id: "track-2", name: "Song 2", artist: "Artist B" }
        ];

        const playlistName = document.getElementById("playlist-name");
        playlistName.value = "Simple Test Playlist";

        const createBtn = document.getElementById("create-playlist-btn");
        createBtn.disabled = false;
        createBtn.classList.remove("bg-gray-300", "cursor-not-allowed");
        createBtn.classList.add("bg-gradient-to-r", "from-indigo-500", "to-pink-500", "text-white");
        """)

    # Now click the button
    create_btn = WebDriverWait(browser, 5).until(
        EC.element_to_be_clickable((By.ID, "create-playlist-btn"))
    )
    browser.execute_script("arguments[0].click();", create_btn)

    # Wait for confirmation section
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.ID, "playlist-output"))
    )

    assert "Your Playlist" in browser.page_source
    print("✅ Playlist creation completed successfully")



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

        # Clean up existing request
        Friend.query.filter_by(user_id=main_user.id, friend_id=friend_user.id).delete()
        db.session.commit()

        main_user_id = main_user.id
        friend_user_id = friend_user.id

    login(browser, live_server_url)

    for route in ['/add-friend', '/friends/add', '/friends/list', '/friends']:
        browser.get(f"{live_server_url}{route}")
        try:
            input_field = find_element_with_multiple_selectors(browser, [
                "[name='friend_username']", "input[type='text']", "input"
            ])

            input_field.clear()
            input_field.send_keys("frienduser")

            for _ in range(3):
                try:
                    add_btn = find_element_with_multiple_selectors(
                        browser,
                        ["[type='submit']", ".btn-submit", "//button[contains(text(), 'Add')]", "//button[contains(text(), 'Send')]"]
                    )
                    browser.execute_script("arguments[0].scrollIntoView(true);", add_btn)
                    add_btn.click()
                    toast = wait_for_toast_or_success(browser)
                    print("Toast:", toast)

                    take_screenshot(browser, "after_friend_click")
                    with open("selenium_screenshots/friend_form.html", "w", encoding="utf-8") as f:
                        f.write(browser.page_source)

                    print("✅ Clicked Add Friend button")
                    break
                except StaleElementReferenceException:
                    time.sleep(1)

            time.sleep(2)
            break
        except Exception as e:
            print(f"⚠️ Error during friend add: {e}")
            continue

    toast = wait_for_toast_or_success(browser)
    print("Toast (if any):", toast)
    take_screenshot(browser, "after_friend_click")

    with app.app_context():
        main_user = db.session.get(User, main_user_id)
        friend_user = db.session.get(User, friend_user_id)
        request = Friend.query.filter_by(user_id=main_user.id, friend_id=friend_user.id).first()
        assert request is not None, "Friend request not found in database"
        print("✅ Friend request recorded in database")
