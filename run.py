# Import the app factory function
from app import create_app

# Create the Flask app instance
app = create_app()

if __name__ == "__main__":
    # Run the Flask app in debug mode
    app.run(debug=True)