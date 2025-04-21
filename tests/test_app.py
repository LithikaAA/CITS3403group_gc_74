import unittest
from app import create_app, db
from app.models import User
import os
print("Current working directory:", os.getcwd())

class FlaskAppTestCase(unittest.TestCase):
    """
    Test case for the Flask application.
    """
    def setUp(self):
        """
        Set up the test environment.
        """
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory database for testing
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        with self.app.app_context():
            db.create_all()  # Create database tables

        self.client = self.app.test_client()

    def tearDown(self):
        """
        Clean up the test environment.
        """
        with self.app.app_context():
            db.session.remove()
            db.drop_all()  # Drop all tables

    def test_intro_page(self):
        """
        Test the intro page (home route).
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)  # Replace 'Welcome' with actual content in intro.html

    def test_dashboard_page(self):
        """
        Test the dashboard page.
        """
        response = self.client.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)  # Replace 'Dashboard' with actual content in dashboard.html

    def test_upload_page(self):
        """
        Test the upload page.
        """
        response = self.client.get('/upload')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Upload', response.data)  # Replace 'Upload' with actual content in upload.html

    def test_share_page(self):
        """
        Test the share page.
        """
        response = self.client.get('/share')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Share', response.data)  # Replace 'Share' with actual content in share.html

    def test_index_page(self):
        """
        Test the index page (home route).
        """
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)  # Replace 'Welcome' with actual content in index.html

    def test_login_page(self):
        """
        Test the login page.
        """
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)  # Replace 'Login' with actual content in login.html

    def test_signup_page(self):
        """
        Test the signup page.
        """
        response = self.client.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)  # Replace 'Sign Up' with actual content in signup.html

    def test_signup_and_login(self):
        """
        Test user signup and login functionality.
        """
        # Test signup
        response = self.client.post('/signup', data={
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Test login
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'password123'
        })
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard

if __name__ == '__main__':
    unittest.main()