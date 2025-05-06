import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session
import json
from flask_login import current_user
from app.models import db, Track, UserTrack
from datetime import datetime


upload_bp = Blueprint('upload', __name__)

# ---------- Main Upload Page ----------
@upload_bp.route('/upload', methods=['GET'])
def upload():
    """
    Display the upload page with dynamic username and song count.
    """
    username = session.get('username', 'User')   # Assuming you store username in session

    # Mock: Fetch user's uploaded songs (Replace with DB query in real case)
    user_uploads = {
        'Zi Qian': ['Song 1', 'Song 2', 'Song 3', 'Song 4'],
        'Alice': ['Song A', 'Song B']
    }
    uploaded_songs = user_uploads.get(username, [])
    song_count = len(uploaded_songs)

    return render_template('upload.html', username=username, song_count=song_count)


# ---------- Create Playlist (Manual Entry) ----------
@upload_bp.route('/upload/create-playlist')
def create_playlist():
    """
    Placeholder for creating a playlist manually.
    """
    flash('The "Create Playlist" feature is coming soon!', 'info')
    return redirect(url_for('upload.upload'))


# ---------- Handle CSV Upload ----------
# ---------- Handle JSON Upload ----------
from datetime import datetime  # Make sure this is imported

@upload_bp.route('/upload/upload-json', methods=['POST'])
def upload_json():
    """
    Handle JSON uploads for user listening data.
    """
    file = request.files.get('user_json')

    if not file or file.filename == '' or not file.filename.endswith('.json'):
        flash('No valid JSON file selected. Please choose a .json file.', 'error')
        return redirect(url_for('upload.upload'))

    try:
        data = json.load(file)
        added_or_updated_count = 0

        for entry in data:
            title = entry.get('trackName')
            artist = entry.get('artistName')
            ms_played = entry.get('msPlayed')

            if not title or not artist:
                continue

            # Get or create Track
            track = Track.query.filter_by(title=title, artist=artist).first()
            if not track:
                track = Track(
                    title=title,
                    artist=artist,
                    genre="Unknown",
                    date_played=datetime.utcnow()
                )
                db.session.add(track)
                db.session.flush()  # Gets track.id before commit

            # Check if this user already has this track
            user_track = UserTrack.query.filter_by(user_id=current_user.id, track_id=track.id).first()

            if user_track:
                # Update existing entry
                user_track.times_played += 1
                user_track.total_ms_listened = user_track.times_played * user_track.song_duration
            else:
                # Create new entry
                user_track = UserTrack(
                    user_id=current_user.id,
                    track_id=track.id,
                    song=title,
                    artist=artist,
                    song_duration=ms_played,
                    times_played=1,
                    total_ms_listened=ms_played
                )
                db.session.add(user_track)

            added_or_updated_count += 1

        db.session.commit()
        flash(f"Processed {added_or_updated_count} user song records (inserted/updated).", "success")

    except Exception as e:
        flash(f"Error processing JSON: {str(e)}", "error")

    return redirect(url_for('upload.upload'))
