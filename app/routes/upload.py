import os
from flask import (
    Blueprint, render_template, request, redirect,
    url_for, flash, current_app, session, jsonify
)
from flask_login import current_user
from app.models import db, Track, UserTrack
from app.utils.spotify_auth import search_tracks, get_audio_features

upload_bp = Blueprint('upload', __name__)

# ---------- Main Upload Page ----------
@upload_bp.route('/upload', methods=['GET'])
def upload():
    """
    Display the upload page with dynamic username and song count.
    """
    username = session.get('username', 'User')
    # Replace with actual DB logic later
    song_count = UserTrack.query.filter_by(user_id=current_user.id).count() if current_user.is_authenticated else 0
    return render_template('upload.html', username=username, song_count=song_count)


# ---------- Search Songs (Spotify API) ----------
@upload_bp.route("/api/search-tracks")
def api_search_tracks():
    query = request.args.get("query")
    if not query:
        return jsonify([])
    return jsonify(search_tracks(query))


# ---------- Fetch Audio Features ----------
@upload_bp.route("/api/audio-features", methods=["POST"])
def api_audio_features():
    try:
        data = request.get_json()
        print(f"[DEBUG] Incoming payload: {data}")

        track_ids = data.get("track_ids", [])
        if not isinstance(track_ids, list) or not track_ids:
            return jsonify({'error': 'No valid track_ids provided'}), 400

        features = get_audio_features(track_ids)
        print(f"[DEBUG] Spotify returned: {features}")

        if not features or all(f is None for f in features):
            return jsonify([]), 200

        filtered = [f for f in features if f is not None]
        return jsonify(filtered)
    except Exception as e:
        print(f"[ERROR] get_audio_features failed: {e}")
        return jsonify({'error': str(e)}), 500



# ---------- Playlist Creation Endpoint (POST from frontend later) ----------
@upload_bp.route("/upload/create-playlist", methods=["POST"])
def create_playlist():
    """
    Accepts selected song IDs from the frontend to group into a playlist.
    """
    data = request.get_json()
    tracks = data.get("tracks", [])
    playlist_name = data.get("playlist_name", "Untitled Playlist")

    if not tracks:
        return jsonify({"status": "error", "message": "No tracks provided."}), 400

    for song in tracks:
        title = song.get("name")
        artist = song.get("artist")
        duration = song.get("duration_ms", 0)

        if not title or not artist:
            continue

        track = Track.query.filter_by(title=title, artist=artist).first()
        if not track:
            track = Track(
                title=title,
                artist=artist,
                genre="Unknown",
                date_played=None
            )
            db.session.add(track)
            db.session.flush()

        user_track = UserTrack.query.filter_by(user_id=current_user.id, track_id=track.id).first()
        if not user_track:
            user_track = UserTrack(
                user_id=current_user.id,
                track_id=track.id,
                song=title,
                artist=artist,
                song_duration=duration,
                times_played=1,
                total_ms_listened=duration
            )
            db.session.add(user_track)

    db.session.commit()
    return jsonify({"status": "success", "message": f"Playlist '{playlist_name}' created."})
