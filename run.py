from app import app
import os

app.run(
    debug=os.getenv("FLASK_DEBUG", "False").lower() == "true",
    host=os.getenv("FLASK_RUN_HOST", "127.0.0.1"),
    port=int(os.getenv("FLASK_RUN_PORT", 5000))
)