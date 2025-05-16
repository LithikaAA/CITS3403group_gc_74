import os
from app import create_app, db

# Create the app using the factory
app = create_app()

# Create tables inside app context
with app.app_context():
    db.create_all()

# Run the app
if __name__ == '__main__':
    # Check if running in test mode
    if os.environ.get('FLASK_ENV') == 'testing':
        port = 5000  # Use a fixed port for testing
        # Create the port file that the tests are looking for
        with open('.flask-test-port', 'w') as f:
            f.write(str(port))
        print(f"Running in TEST mode on port {port}")
        app.run(debug=True, port=port, use_reloader=False)
    else:
        # Normal run
        app.run(debug=True)