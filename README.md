# 📀 VibeShare

**VibeShare** is a music insight platform that lets users search for songs via the Spotify API, create playlists, and visualise their listening patterns. This project was developed for the **CITS3403 Web Application Development** unit at the **University of Western Australia**.

---

## 🔍 Features

### 🎵 Song Search

* Search for songs via the Spotify API
* Enriched metadata from a local CSV for robustness and fallback

### 🎧 Playlist Creation

* Search and select songs to build named playlists
* Playlists are saved in the database using a many-to-many join (`PlaylistTrack`)
* Collapsible UI shows included songs under each playlist

### 📊 Visualisation Dashboard

* Explore moods, tempo, energy, and more via interactive Chart.js graphs
* Select your playlist to fetch data from `/upload/playlist/<playlist_id>/tracks`
* Charts include:

  * Mood radar
  * Tempo distribution
  * Danceability vs Energy
  * Mode (Major/Minor) comparison
  * Valence vs Acousticness (quadrant plot)
  * Top artists and summary statistics

### 🔁 Data Sharing (Secure)

* Friend-based sharing: compare your data with accepted friends
* Only shows playlists from users who’ve shared with you
* Friend dropdown dynamically loads available shared data

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
├── models.py             # SQLAlchemy models
├── routes/               # Flask Blueprints
├── templates/            # Jinja2 templates
├── static/               # Tailwind, JS, images
├── utils/                # API wrappers & helpers
├── migrations/           # Alembic files
├── config.py             # Flask config
├── run.py                # App entry
├── requirements.txt      # Dependencies
├── .env / .env.example   # Environment config
└── seed_data.py          # Seed script for test data
```

---

## 🛠️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/LithikaAA/CITS3403group_gc_74.git
cd CITS3403group_gc_74
```

### 2. Create virtual environment and install dependencies

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Set environment variables

Create a `.env` file and include:

```env
SPOTIPY_CLIENT_ID=your_client_id
SPOTIPY_CLIENT_SECRET=your_client_secret
SPOTIPY_REDIRECT_URI=http://127.0.0.1:5000/callback
SECRET_KEY=your_flask_secret
```

> You can use `.env.example` as a template.

⚠️ **Security Note:** Never commit your `.env` or real credentials to GitHub. Use this file for development only.

---

### 4. Initialise the database

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

#### ↺ Fallback if migration errors occur:

```bash
rm -f instance/app.db
flask db stamp head
flask db upgrade
```

---

### 5. Seed with demo/test data

```bash
python seed_data.py
```

Or via Flask shell:

```bash
flask shell
>>> from seed_data import main
>>> main()
```

---

### 6. Run the Flask app

```bash
flask run
```

---

## 👤 Test Account (For Markers)

```
Username: marker123
Password: testmarker
```

### State of marker123 account:

* **Friends (shared playlists):** `vmontes`, `steven12`, `cmartinez`, `raymond89`
* **Incoming requests:** `vmiller`, `cruzdenise`, `pagetamara`, `connie96`
* **Outgoing request:** `hobbsmatthew`
* **Marker playlists:**

  * `Marker's Mood Mix` (low valence)
  * `Marker's Energy Set` (high energy)
* Each accepted friend has shared 2 playlists (8 songs each)

---

## 🧰 Testing Guide

### ✅ Unit Tests

* Location: `tests/test_app.py`
* Covers:

  * Signup, login, logout
  * Playlist creation & deletion
  * Friend requests
  * Access control and route validation

Run with:

```bash
python tests/test_app.py
```

---

### 👡️ Selenium UI Tests (Basic)

* Location: `tests/test_selenium_ui.py`
* Simulates:

  * User signup
  * Login/logout flow
  * Flash messages for invalid inputs

Run in **two terminals**:

```bash
# Terminal 1:
flask run

# Terminal 2:
python tests/test_selenium_ui.py
```

> ✅ Chrome browser is required. Enable `--headless` in the file for headless mode.

---

### 🥰 Selenium Flow Tests (Advanced)

* Location: `tests/selenium_tests/test_selenium_flows.py`
* Tests:

  * Playlist creation with validations
  * Sending/receiving friend requests
  * Navigation, flash messages, and state updates

Run via:

```bash
python tests/selenium_tests/test_selenium_flows.py
```

---

## 👨‍💻 Team Members

| Name             | GitHub Username |
| ---------------- | --------------- |
| Zi Qian Tan      | Squirtl3-Nee    |
| Lithika          | LithikaAA       |
| Kylan Gillmore   | KylanGillmore   |
| Adrian Gonsalves | Adundo123       |

---

## 📌 License

This project is for **educational purposes only**. Built for **CITS3403 Web Application Development** at the **University of Western Australia**.
