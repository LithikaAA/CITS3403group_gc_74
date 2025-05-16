# VibeShare

**VibeShare** is a music insight platform that lets users search for songs via the Spotify API, create playlists, and visualise their listening patterns. This project was developed as part of the CITS3403 Web Application Development unit at UWA.

---

## 🔍 Features

### 🎵 Song Search

- Search for songs using the Spotify API
- Enriched metadata from a local CSV for robustness and fallback

### 🎧 Playlist Creation

- Select and add songs to create named playlists
- Playlists and tracks are persisted in the database using a many-to-many relationship
- Collapsible containers display track lists for each playlist

### 📊 Visualisation Dashboard

- Interactive charts powered by Chart.js
- Filter by your playlists from a dropdown menu (`/upload/my-playlists`)
- Dynamically visualise playlist data via `/upload/playlist/<playlist_id>/tracks`
- Chart types include:
  - Mood radar
  - Tempo distribution
  - Danceability vs Energy
  - Mode comparison (Major/Minor)
  - Valence vs Acousticness (Quadrant plot)
  - Top artists and summary statistics

### 🔁 Data Sharing (Secure)

- Compare your data with accepted friends
- Only shows playlists that friends have explicitly shared with you
- Friend playlist comparison dropdown dynamically loads from shared data

---

## ⚙️ Tech Stack

| Layer          | Technology                            |
| -------------- | ------------------------------------- |
| Frontend       | HTML, CSS, TailwindCSS, JavaScript    |
| Backend        | Python (Flask)                        |
| Database       | SQLite with SQLAlchemy ORM            |
| Authentication | Flask-Login                           |
| Visualisation  | Chart.js / JavaScript-based libraries |

---

## 📁 Project Structure

```
app/
├── models.py             # SQLAlchemy models (User, Track, Playlist, PlaylistTrack, Share, etc.)
├── routes/               # Modular blueprint routes (auth, index, upload, share)
├── templates/            # Jinja2 templates (upload, dashboard, shared_dashboard, etc.)
├── static/               # TailwindCSS, JavaScript, assets (components/, css/, img/, js/)
├── utils/                # Spotify API wrappers and feature-loading utilities
├── migrations/           # Alembic migration files
├── app.db                # SQLite database file (instance/app.db)
├── config.py             # App configuration
├── run.py                # Flask entry point
├── requirements.txt      # Python dependencies
├── .env / .env.example   # Environment configuration
└── seed_data.py          # Script to seed test data
```


---

## 🧪 Running the App Locally

### 1. **Clone the Repository**

```bash
git clone <https://github.com/LithikaAA/CITS3403group_gc_74.git>
cd VibeShare
```
2. Create Virtual Environment and Install Dependencies
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
pip install -r requirements.txt
```

3. Set Up Environment Variables
Create a .env file and include your Spotify credentials:

```dotenv
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SECRET_KEY=your_flask_secret
```
You can use .env.example as a template.

4. Set Up the Database
```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

5. Seed the App with Demo/Test Data
```bash
python seed_data.py
```
Or from Flask shell:

```bash

flask shell
>>> from seed_data import main
>>> main()

```

6. Run the Flask App
```bash
flask run
```


##👤 Test Account (Marker)
To assist with testing, use the following test account:

```makefile
Username: marker123
Password: testmarker
```

### Marker Account Setup
* Friends (shared playlists): vmontes, steven12, cmartinez, raymond89

* Incoming Requests: vmiller, cruzdenise, pagetamara, connie96

* Outgoing Request: hobbsmatthew

* Marker Playlists:
 
 * Marker's Mood Mix (low valence)
 
 * Marker's Energy Set (high energy)

* Each friend has shared 2 playlists of 8 songs each with the marker

##🧪 Testing Guide

###✅ Unit Tests
Location: tests/test_app.py

Covers:
* Signup, login, logout
* Playlist creation & deletion
* Friend requests
* Route access & validation

Run with:

```bash
python tests/test_app.py
```

###🖱️ Selenium UI Tests (Basic)
Location: tests/test_selenium_ui.py

Covers:
* User signup
* Login/logout flow
* Error handling (duplicate accounts, invalid login)

Run in two terminals:

Terminal 1 (run the app):

```bash
flask run
```

Terminal 2 (run Selenium tests):

```bash
pip install selenium webdriver-manager
python tests/test_selenium_ui.py
```
> Chrome must be installed. For headless mode, uncomment the --headless config in the test file.

###🧪 Selenium Flow Tests (Advanced)
Location: tests/selenium_tests/test_selenium_flows.py

Covers:
 *Playlist creation via UI
 *Song search and validation feedback
 *Sending friend requests
 *Accepting friend requests
 *Navigation between pages
 *Flash messages and error prompts

Steps to run:

1. Start the app in one terminal:

```bash
flask run
```

2. Run the Selenium flow tests in another:

```bash
python tests/selenium_tests/test_selenium_flows.py
```
> If you encounter any browser interaction issues, make sure Chrome is updated and that you're not blocking popups or alerts.

## Team Members

| Name             | GitHub Username |
| ---------------- | --------------- |
| Zi Qian Tan      | Squirtl3-Nee    |
| Lithika          | LithikaAA       |
| Kylan Gillmore   | KylanGillmore   |
| Adrian Gonsalves | Adundo123       |

##📜 License
This project is for educational purposes only. Developed for CITS3403 Web Application Development at the University of Western Australia.



