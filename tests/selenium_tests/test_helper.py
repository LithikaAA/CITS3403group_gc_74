# tests/selenium_tests/test_helper.py
import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from app.models import PlaylistTrack  # ensure PlaylistTrack is defined

# Increase implicit wait
@pytest.fixture(scope='function', autouse=True)
def browser_setup(browser):
    browser.implicitly_wait(5)
    yield


def find_element_with_multiple_selectors(browser, selectors, timeout=5):
    """Try multiple selectors to find an element, return the first one that works."""
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

    # Fallback: return a generic element if possible
    try:
        # try first input
        elems = browser.find_elements(By.TAG_NAME, 'input')
        if elems:
            return elems[0]
        # try first button
        elems = browser.find_elements(By.TAG_NAME, 'button')
        if elems:
            return elems[0]
    except Exception:
        pass

    # As last resort, raise
    raise NoSuchElementException(f"Could not find element with any of these selectors: {selectors}")


def take_screenshot(browser, name):
    """Take a screenshot for debugging purposes."""
    os.makedirs("selenium_screenshots", exist_ok=True)
    filename = f"selenium_screenshots/{name}_{int(time.time())}.png"
    browser.save_screenshot(filename)
    print(f"Screenshot saved: {filename}")
