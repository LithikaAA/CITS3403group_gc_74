from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    app.run(
        debug=os.getenv("FLASK_DEBUG", "False").lower() == "true",
        host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_RUN_PORT", "5000"))  # Added quotes around 5000
    )