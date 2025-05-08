# VibeShare

**VibeShare** is a music insight platform that lets users search for songs via the Spotify API, create playlists, and visualise their listening patterns. This project was developed as part of the CITS3403 Web Application Development unit.

## Features

### Song Search
- Integrated with Spotify API to search for tracks
- Enriched metadata from local CSV for robustness

### Playlist Creation
- Users can search and select multiple songs
- Create a named playlist stored in the database
- Backend persists tracks via a many-to-many `PlaylistTrack` join table
- Supports collapsible playlist containers that display included songs after creation

### Visualisation Dashboard
- Explore mood, tempo, and energy via interactive charts (Chart.js)
- Filter by playlist using a dropdown menu populated via `/upload/my-playlists`
- On selection, data is fetched from `/upload/playlist/<playlist_id>/tracks` and visualised
- Charts include:
  - Mood radar
  - Tempo distribution
  - Danceability vs Energy
  - Mode (Major/Minor) comparison
  - Valence vs Acousticness Quadrant Plot 
  - Top Artists and Summary Stats

### Data Sharing (Secure)
- Dashboard supports "You vs Friend" comparisons
- Only includes data from friends who have shared access
- Dropdown populated with friend playlist data for comparison

## Tech Stack

| Layer         | Technology                             |
|--------------|-----------------------------------------|
| Frontend     | HTML, CSS, Bootstrap, JavaScript        |
| Backend      | Python (Flask)                          |
| Database     | SQLite with SQLAlchemy ORM              |
| Authentication | Flask-Login                           |
| Visualisation | Chart.js / JavaScript-based libraries  |

## Project Structure

```bash
app/
├── models.py             # SQLAlchemy models (User, Track, Playlist, PlaylistTrack, Share, etc.)
├── upload.py             # Track search, enrichment, playlist creation endpoints
├── dashboard.py          # Visualisation routes for authenticated users
├── share.py              # Handles sharing logic
├── templates/            # Jinja2 templates for HTML rendering
│   ├── upload.html       # Song search and playlist creation
│   ├── dashboard.html    # Dashboard visualisation interface
│   ├── shared_dashboard.html  # View friend’s shared data
│   └── ...
├── static/               # TailwindCSS, JavaScript, assets
│   ├── components/       # JS modules for navbar, breadcrumbs
│   ├── css/              # Global styling
│   └── img/              # Image assets
├── utils/                # Spotify API wrappers and feature loading
├── routes/               # Modular blueprint routes (auth, index, upload, share)
├── app.db                # SQLite database file
├── migrations/           # Alembic migration files
├── requirements.txt      # Python dependencies
├── .env / .env.example   # Environment config files
├── run.py                # Flask entry point
└── config.py             # App configuration
```

## Setup Instructions

1. **Clone the repository**
2. Install dependencies:
```bash
pip install -r requirements.txt
```
3. Initialise the database:
```bash
flask db init
flask db migrate -m "Initial tables"
flask db upgrade
```
4. Run the Flask app:
```bash
flask run
```

> **Note**: Markers should use the test account provided for login. Spotify API client credentials are required to enable the search functionality.

## Team Members

| Name             | GitHub Username   |
|------------------|-------------------|
| Zi Qian Tan      | Squirtl3-Nee      |
| Lithika          | LithikaAA         |
| Kylan Gillmore   | KylanGillmore     |
| Adrian Gonsalves | Adundo123         |

## License
This project is for educational use only. Built for CITS3403 at UWA.
