import unittest
import time
from app import create_app, db
from app.models import User, Playlist
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from datetime import datetime

class SeleniumTests(unittest.TestCase): 
    def setUp(self):
        self.driver = webdriver.Chrome()
        self.driver.implicitly_wait(5)
        # Setup test user in the database
        self.app = create_app()
        self.app.app_context().push()
        db.create_all()
        # Remove test user if exists
        User.query.filter_by(username="seleniumuser").delete()
        User.query.filter_by(username="existinguser").delete()
        db.session.commit()
        # Create an existing user for duplicate test
        user = User(username="existinguser", email="existing@example.com")
        user.set_password("password123")
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        self.driver.quit()
        db.session.remove()
        db.drop_all()

    def test_signup_success(self):
        self.driver.get("http://localhost:5000/auth/signup")
        self.driver.find_element(By.NAME, "username").send_keys("seleniumuser")
        self.driver.find_element(By.NAME, "email").send_keys("seleniumuser@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        self.driver.find_element(By.ID, "terms").click()
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        # Should redirect to login with flash message
        self.assertIn("login", self.driver.current_url)
        self.assertIn("Account created successfully! Please log in.", self.driver.page_source)

    def test_signup_existing_user(self):
        self.driver.get("http://localhost:5000/auth/signup")
        self.driver.find_element(By.NAME, "username").send_keys("existinguser")
        self.driver.find_element(By.NAME, "email").send_keys("existing@example.com")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        self.driver.find_element(By.ID, "terms").click()
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        # Should stay on signup and show error
        self.assertIn("signup", self.driver.current_url)
        self.assertIn("Username or email already exists.", self.driver.page_source)
        
    def test_login_success(self):
        self.driver.get("http://localhost:5000/auth/login")
        self.driver.find_element(By.NAME, "identifier").send_keys("existinguser")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        # Should redirect to dashboard
        self.assertIn("/dashboard", self.driver.current_url)
        self.assertIn("Dashboard", self.driver.page_source)  # Adjust if your dashboard has a different heading

    def test_login_failure(self):
        self.driver.get("http://localhost:5000/auth/login")
        self.driver.find_element(By.NAME, "identifier").send_keys("wronguser")
        self.driver.find_element(By.NAME, "password").send_keys("wrongpass")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)
        # Should stay on login and show error
        self.assertIn("login", self.driver.current_url)
        self.assertIn("Invalid username/email or password.", self.driver.page_source)
    
    def test_dashboard_requires_login(self):
        """Unlogged user should get sent to login when accessing /dashboard."""
        self.driver.get("http://localhost:5000/dashboard")
        time.sleep(1)
        self.assertIn("/auth/login", self.driver.current_url)
        self.assertIn("Please log in to access this page.", self.driver.page_source)

    def test_logout_flow(self):
        """After login, clicking ‘Logout’ should send you back to the login page."""
        # 1) log in first
        self.driver.get("http://localhost:5000/auth/login")
        self.driver.find_element(By.NAME, "identifier").send_keys("existinguser")
        self.driver.find_element(By.NAME, "password").send_keys("password123")
        self.driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        time.sleep(1)

        # 2) simply navigate to the logout URL
        self.driver.get("http://localhost:5000/auth/logout")
        time.sleep(1)

        # 3) verify redirect and flash
        self.assertIn("/auth/login", self.driver.current_url)
        self.assertIn("You have been logged out.", self.driver.page_source)
        
    
     
if __name__ == "__main__":
    unittest.main()
