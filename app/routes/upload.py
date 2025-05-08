import os
from flask import (
    Blueprint, render_template, request, session, jsonify
)
from flask_login import current_user
from app.models import db, Track, UserTrack
from app.utils.spotify_auth import search_tracks
from app.utils.track_feature_loader import get_track_features_by_id

upload_bp = Blueprint('upload', __name__)

# ---------- Main Upload Page ----------
@upload_bp.route('/upload', methods=['GET'])
def upload():
    username = session.get('username', 'User')
    song_count = UserTrack.query.filter_by(user_id=current_user.id).count() if current_user.is_authenticated else 0
    return render_template('upload.html', username=username, song_count=song_count)


# ---------- Search Songs (Spotify API + CSV metadata) ----------
@upload_bp.route("/api/search-tracks")
def api_search_tracks():
    query = request.args.get("query")
    if not query:
        return jsonify([])

    results = search_tracks(query)
    enriched_results = []

    for track in results:
        track_id = track.get("id")
        enriched = get_track_features_by_id(track_id)

        if enriched:
            # Merge Spotify API and CSV metadata
            track.update({
                "genre": enriched.get("genre"),
                "duration_ms": enriched.get("duration_ms"),
                "danceability": enriched.get("danceability"),
                "energy": enriched.get("energy"),
                "liveness": enriched.get("liveness"),
                "acousticness": enriched.get("acousticness"),
                "valence": enriched.get("valence"),
                "tempo": enriched.get("tempo"),
                "mode": enriched.get("mode")
            })

        enriched_results.append(track)

    return jsonify(enriched_results)

@upload_bp.route("/upload/create-playlist", methods=["POST"])
def create_playlist():
    data = request.get_json()
    playlist_name = data.get("playlist_name", "Untitled Playlist")
    tracks = data.get("tracks", [])

    if not tracks:
        return jsonify({"status": "error", "message": "No tracks provided."}), 400

    print(f"[DEBUG] Mock saving playlist '{playlist_name}' with {len(tracks)} songs.")
    return jsonify({"status": "success", "message": f"Playlist '{playlist_name}' created."})

