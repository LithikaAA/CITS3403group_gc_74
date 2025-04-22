# 🎵 VibeShare

**VibeShare** is a web-based music data sharing platform that allows users to upload their Spotify listening history, visualise their music preferences, and selectively share insights with friends. Whether you're comparing your favourite tracks or discovering new genres through your social circle, VibeShare helps you explore music in a more connected and engaging way.

---

## 🚀 Features

- **🔐 User Authentication**  
  Secure sign-up and log-in functionality using Flask-Login.

- **📁 Data Upload**  
  Upload your Spotify listening history via exported data from Spotify or publicly available Kaggle datasets.

- **📊 Data Visualisation**  
  Explore your top artists, tracks, genres, and listening trends through dynamic and interactive charts.

- **🤝 Data Sharing**  
  Share your data with specific users and explore data that others have shared with you.

- **📈 Personal Dashboard**  
  Track listening durations, genre preferences, time-of-day habits, and more in a personalised view.

- **🌐 Friendship Network**  
  Connect with other users to exchange music tastes and discover what your friends are listening to.

---

## 🧱 Tech Stack

| Layer        | Technology                    |
|--------------|-------------------------------|
| Frontend     | HTML, CSS, Bootstrap, JavaScript |
| Backend      | Python (Flask)                |
| Database     | SQLite with SQLAlchemy ORM    |
| Authentication | Flask-Login                 |
| Visualisation | Chart.js / JavaScript-based libraries |

---

## 📂 Project Structure

```plaintext
vibeshare/
├── app/
│   ├── __init__.py                  # App factory, loads .env, sets up Flask app
│   ├── models.py                    # SQLAlchemy models (User, Track, Playlist, etc.)
│   ├── routes/                      # Folder for modular route handlers
│   │   ├── auth.py                  # Login, logout, signup routes
│   │   ├── dashboard.py             # Main user dashboard routes
│   │   ├── upload.py                # Upload and handle CSV/audio data
│   │   ├── share.py                 # Sharing tracks/playlists with other users
│   ├── templates/                   # HTML files rendered with Jinja
│   │   ├── base.html                # Base layout (nav/footer)
│   │   ├── index.html               # Welcome / landing page
│   │   ├── login.html               # Login form
│   │   ├── signup.html              # Registration form
│   │   ├── dashboard.html           # Main dashboard (top tracks, stats)
│   │   ├── upload.html              # Upload music or CSV data
│   │   ├── share.html               # Share music with friends
│   ├── static/                      # Static files (CSS, JS, images)
│   │   ├── css/
│   │   │   └── style.css            # Custom styles (if any)
│   │   ├── js/
│   │   │   └── app.js               # Optional JS logic or AJAX
│   │   ├── img/
│   │   │   └── logo.png             # App logo or album art
├── data/                            # Local data not tracked by Git
│   └── spotify.csv                  # ✅ Your downloaded Kaggle data (gitignored)
├── tests/                           # Unit and Selenium tests
│   └── test_app.py                  # Example test (login, DB, etc.)
├── deliverables/                    # Reports, screenshots for submission
├── run.py                           # Entry point to run the Flask app
├── .env                             # Your local config (SECRET_KEY, etc.) [gitignored]
├── .env.example                     # ✅ Shared template of environment variables
├── requirements.txt                 # All necessary Python packages
├── README.md                        # Project description and setup instructions
└── .gitignore                       # Ignore virtual env, .env, data/, etc.
