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

vibeshare/
├── app/
│   ├── init.py                  # Python file to initialize the app
│   ├── models.py                    # Python file for database models
│   ├── routes/                      # Folder for route files
│   │   ├── auth.py                  # Routes for authentication (login/signup)
│   │   ├── dashboard.py             # Routes for user dashboard
│   │   ├── upload.py                # Routes for data upload
│   │   ├── share.py                 # Routes for data sharing
│   ├── templates/                   # Folder for HTML template files
│   │   ├── index.html               # Landing page
│   │   ├── login.html               # Login page
│   │   ├── signup.html              # Signup page
│   │   ├── dashboard.html           # Dashboard page
│   │   ├── upload.html              # Upload page
│   │   ├── share.html               # Share data page
│   ├── static/                      # Folder for static files (CSS, JS, images)
│   │   ├── css/
│   │   │   └── style.css            # Custom CSS styles
│   │   ├── js/
│   │   │   └── app.js               # Custom JavaScript file
│   │   ├── img/
│   │   │   └── logo.png             # Logo image
├── tests/                           # Folder for unit tests
│   └── test_app.py                  # Example test file
├── deliverables/                    # Folder for project deliverables (e.g., reports)
├── run.py                           # Main Python file to start the app
├── requirements.txt                 # Text file for Python package dependencies
├── README.md                        # Markdown file with project documentation
└── .gitignore                       # Git ignore file for excluding unnecessary files 

