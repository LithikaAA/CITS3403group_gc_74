# VibeShare

**VibeShare** is a music insight platform that lets users search for songs via the Spotify API, create playlists, and visualise their listening patterns. This project was developed as part of the CITS3403 Web Application Development unit at UWA.

---

## Features

### Song Search

* Integrated with the Spotify API to search for tracks
* Enriched metadata from a local CSV for robustness

### Playlist Creation

* Users can search and select multiple songs
* Create a named playlist stored in the database
* Backend persists tracks via a many-to-many `PlaylistTrack` join table
* Supports collapsible playlist containers that display included songs after creation

### Visualisation Dashboard

* Explore mood, tempo, and energy via interactive charts (Chart.js)
* Filter by playlist using a dropdown menu populated from `/upload/my-playlists`
* On selection, data is fetched from `/upload/playlist/<playlist_id>/tracks` and visualised
* Charts include:

  * Mood radar
  * Tempo distribution
  * Danceability vs Energy
  * Mode (Major/Minor) comparison
  * Valence vs Acousticness quadrant plot
  * Top artists and summary statistics

### Data Sharing (Secure)

* Dashboard supports “You vs Friend” comparisons
* Only includes data from friends who have granted access
* Comparison dropdown populated with friends’ shared playlist data

---

## Tech Stack

| Layer          | Technology                            |
| -------------- | ------------------------------------- |
| Frontend       | HTML, CSS, TailwindCSS, JavaScript    |
| Backend        | Python (Flask)                        |
| Database       | SQLite with SQLAlchemy ORM            |
| Authentication | Flask-Login                           |
| Visualisation  | Chart.js / JavaScript-based libraries |

---

## Project Structure

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

## Setup Instructions

1. **Clone the repository**

   ```bash
   git clone <repo_url>
   cd VibeShare
   ```
2. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```
3. **Initialise the database**

   ```bash
   flask db init
   flask db migrate -m "Initial tables"
   flask db upgrade
   ```
4. **Run the Flask app**

   ```bash
   flask run
   ```

> **Note:** Spotify API client credentials are required. Set `SPOTIPY_CLIENT_ID` and `SPOTIPY_CLIENT_SECRET` in your `.env` file.

---

## Testing

### Unit Tests

* Located in `tests/test_app.py`
* Covers core backend features using Flask’s test client:

  * Signup and login flows
  * Dashboard and upload route access
  * Friend request system
  * Playlist creation, validation, and removal

Run unit tests:

```bash
# Ensure virtual environment is activated
python tests/test_app.py
```

### Selenium UI Tests

* Located in `tests/test_selenium_ui.py`
* Simulates user interactions in a real browser:

  * Signup success and duplicate error handling
  * Login with valid/invalid credentials
  * Redirects and flash message visibility
  * Logout flow

Run UI tests:

1. In Terminal 1, start the Flask server:

   ```bash
   flask run
   ```
2. In Terminal 2, run:

   ```bash
   pip install selenium webdriver-manager
   python tests/test_selenium_ui.py
   ```

> Chrome browser is required. Uncomment `--headless` in `tests/test_selenium_ui.py` for headless mode.

---

## Test Account (Marker)

A dedicated test user is provided for markers:

```
Username: marker123
Password: testmarker
```

### Expected State for `marker123`

* **Friends:** `vmontes`, `steven12`, `cmartinez`, `raymond89` (4 accepted friends)
* **Incoming requests:** `vmiller`, `cruzdenise`, `pagetamara`, `connie96` (pending)
* **Outgoing request:** `hobbsmatthew`
* **Shared playlists:** 8 playlists (2 from each accepted friend) visible on “View Data” and “Friends” pages
* **Marker’s own playlists:**

  * `Marker's Mood Mix` (valence < 0.4)
  * `Marker's Energy Set` (energy > 0.7)

---

## Seeder and Test Data

Seed data script will wipe and recreate the database (development only).

```bash
# From project root
python seed_data.py
```

Or via Flask shell:

```bash
flask shell
>>> from seed_data import main
>>> main()
```

---

## Team Members

| Name             | GitHub Username |
| ---------------- | --------------- |
| Zi Qian Tan      | Squirtl3-Nee    |
| Lithika          | LithikaAA       |
| Kylan Gillmore   | KylanGillmore   |
| Adrian Gonsalves | Adundo123       |

---

## License

This project is for educational use only. Built for CITS3403 at the University of Western Australia.
