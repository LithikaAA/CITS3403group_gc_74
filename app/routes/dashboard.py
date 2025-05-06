from flask import Blueprint, render_template, session, redirect, url_for
from app.models import db, User, UserTrack, Track
from flask import jsonify
import spotipy
import json
from flask_login import current_user
from sqlalchemy import func

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

        # Fetch top 10 tracks by total listening time
    user_tracks = (
        db.session.query(UserTrack, Track)
        .join(Track, UserTrack.track_id == Track.id)
        .filter(UserTrack.user_id == current_user.id)
        .order_by(UserTrack.total_ms_listened.desc())
        .limit(5)
        .all()
    )

    minutes_by_track = {
        "labels": [ut.song for ut, _ in user_tracks],
        "data": [round(ut.total_ms_listened / 60000, 2) for ut, _ in user_tracks]
    }

    # Query danceability, energy, and play time (converted to minutes)
    danceability_energy_tracks = (
        db.session.query(Track.danceability, Track.energy, UserTrack.total_ms_listened)
        .join(UserTrack, Track.id == UserTrack.track_id)
        .filter(UserTrack.user_id == current_user.id)
        .all()
    )

    danceability_energy = {
        "data": [
            {
                "x": round(danceability or 0, 2),
                "y": round(energy or 0, 2),
                "r": max(3, round(ms / 60000))  # Bubble radius = minutes played
            }
            for danceability, energy, ms in danceability_energy_tracks
        ]
    }

    # Calculate average mood attributes for the user's listened tracks
    mood_attributes = (
        db.session.query(
            func.avg(Track.danceability),
            func.avg(Track.energy),
            func.avg(Track.valence),
            func.avg(Track.acousticness),
            func.avg(Track.liveness)
        )
        .select_from(UserTrack)
        .join(Track, UserTrack.track_id == Track.id)
        .filter(UserTrack.user_id == current_user.id)
        .first()
    )

    # Unpack safely with fallback to 0 if any value is None
    mood_profile = {
        "data": [round(attr or 0, 2) for attr in mood_attributes]
    }


    # Query total listening time (in minutes) by track mode
    mode_minutes = (
        db.session.query(
            Track.mode,
            func.sum(UserTrack.total_ms_listened).label("total_ms")
        )
        .select_from(UserTrack)
        .join(Track, UserTrack.track_id == Track.id)
        .filter(UserTrack.user_id == current_user.id)
        .group_by(Track.mode)
        .all()
    )

    # Initialize counts
    mode_counts = {0: 0, 1: 0}

    # Fill in with actual values
    for mode_val, total_ms in mode_minutes:
        mode_counts[mode_val] = round((total_ms or 0) / 60000, 2)

    # Prepare for Chart.js
    mode = {
        "data": [mode_counts[1], mode_counts[0]]  # [Major, Minor]
    }


    # Step 1: Get top song (by total listening time)
    top_song = (
        db.session.query(UserTrack.song)
        .filter(UserTrack.user_id == current_user.id)
        .order_by(UserTrack.total_ms_listened.desc())
        .first()
    )

    # Step 2: Get total time listened in minutes
    total_ms_listened = (
        db.session.query(func.sum(UserTrack.total_ms_listened))
        .filter(UserTrack.user_id == current_user.id)
        .scalar()
    )
    total_minutes = round((total_ms_listened or 0) / 60000, 2)

    # Step 3: Get weighted average tempo
    weighted_avg_tempo = (
        db.session.query(
            (func.sum(Track.tempo * UserTrack.total_ms_listened) / func.sum(UserTrack.total_ms_listened))
        )
        .select_from(UserTrack)  # <-- this is the fix
        .join(Track, UserTrack.track_id == Track.id)
        .filter(UserTrack.user_id == current_user.id)
        .scalar()
    )
    avg_tempo = round(weighted_avg_tempo or 0)

    top_tracks = {
        "most_played": top_song[0] if top_song else "N/A",
        "total_minutes": total_minutes,
        "avg_tempo": avg_tempo
    }
    
    top_artists_query = (
        db.session.query(
            UserTrack.artist,
            func.sum(UserTrack.total_ms_listened).label("total_ms")
        )
        .filter(UserTrack.user_id == current_user.id)
        .group_by(UserTrack.artist)
        .order_by(func.sum(UserTrack.total_ms_listened).desc())
        .limit(5)
        .all()
    )

    # Extract just the artist names
    top_artists = [artist for artist, _ in top_artists_query]

    # Step 4: Get Top Mood
    major = mode_counts[1]
    minor = mode_counts[0]

    return render_template(
        'dashboard.html',
        username=session.get('username'),
        summary=summary,
        minutes_by_track=minutes_by_track,
        danceability_energy=danceability_energy,
        mood_profile=mood_profile,
        mode=mode,
        top_tracks=top_tracks,
        top_artists=top_artists ,
        major=major,
        minor=minor
)


@dashboard_bp.route('/test-data')
def test_data():
    users = User.query.all()
    return render_template('test_data.html', users=users)


@dashboard_bp.route('/spotify-json')
def spotify_json():
    token_info = session.get('spotify_token')
    sp = spotipy.Spotify(auth=token_info['access_token'])
    top_tracks = sp.current_user_top_tracks(limit=10)
    return jsonify(top_tracks)

@dashboard_bp.route('/spotify-json-simplified')
def spotify_json_simplified():
    token_info = session.get('spotify_token')
    if not token_info:
        return redirect(url_for('auth.login_spotify'))

    sp = spotipy.Spotify(auth=token_info['access_token'])
    results = sp.current_user_top_tracks(limit=10)

    # Extract artist and track name
    simplified = [
        {
            "track": item["name"],
            "artist": ", ".join([artist["name"] for artist in item["artists"]])
        }
        for item in results["items"]
    ]

    # Pass JSON as a string to the template
    json_string = json.dumps(simplified, indent=2)
    return jsonify(json_string)