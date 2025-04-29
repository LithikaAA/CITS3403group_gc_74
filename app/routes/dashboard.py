from flask import Blueprint, render_template, session, redirect, url_for
from app.models import User

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    """
    Render the user dashboard.
    """
    if 'user_id' not in session:
        # Redirect to login if the user is not logged in
        return redirect(url_for('auth.login'))

    # Debugging: Print session data
    print("Session data:", session)

    # Mock Data for Summary Cards
    summary = {
        "total_songs": 1245,
        "total_hours": 312,
        "unique_artists": 98,
        "top_genre": "Pop"
    }

    # Mock Data for Bar Chart (Minutes Played by Track)
    minutes_by_track = {
        "labels": ["Blinding Lights", "Levitating", "Shape of You", "Anti-Hero", "God's Plan"],
        "data": [120, 95, 85, 75, 60]
    }

    # Mock Data for Bubble Chart (Danceability vs Energy)
    danceability_energy = {
        "data": [
            {"x": 0.8, "y": 0.9, "r": 15},  # Example: Blinding Lights
            {"x": 0.7, "y": 0.8, "r": 12},  # Example: Levitating
            {"x": 0.6, "y": 0.7, "r": 10},  # Example: Shape of You
            {"x": 0.5, "y": 0.6, "r": 8},   # Example: Anti-Hero
            {"x": 0.4, "y": 0.5, "r": 6}    # Example: God's Plan
        ]
    }

    # Mock Data for Radar Chart (Mood Profile)
    mood_profile = {
        "data": [0.8, 0.7, 0.6, 0.5, 0.4]  # Example: Danceability, Energy, Valence, Acousticness, Liveness
    }

    # Mock Data for Stacked Bar Chart (Mode Analysis)
    mode = {
        "data": [300, 200]  # Example: Major, Minor
    }

    # Mock Data for Top Tracks
    top_tracks = {
        "most_played": "Blinding Lights",
        "total_minutes": 1200,
        "avg_tempo": 120
    }

    return render_template(
        'dashboard.html',
        username=session.get('username'),
        summary=summary,
        minutes_by_track=minutes_by_track,
        danceability_energy=danceability_energy,
        mood_profile=mood_profile,
        mode=mode,
        top_tracks=top_tracks
    )


@dashboard_bp.route('/test-data')
def test_data():
    users = User.query.all()
    return render_template('test_data.html', users=users)