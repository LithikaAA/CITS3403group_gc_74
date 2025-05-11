import os
from flask import (
    Blueprint, render_template, request, session, jsonify
)
from flask_login import current_user
from app.models import db, Track, UserTrack
from app.utils.spotify_auth import search_tracks
from app.utils.track_feature_loader import get_track_features_by_id
from datetime import datetime

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

# ---------- Create Playlist ----------
@upload_bp.route("/upload/create-playlist", methods=["POST"])
def create_playlist():
    if not current_user.is_authenticated:
        return jsonify({"status": "error", "message": "User not authenticated"}), 403

    # Add debug logging to help diagnose issues
    print("Request received:", request.method)
    print("Content-Type:", request.headers.get('Content-Type'))
    
    try:
        data = request.get_json()
        print("Received data:", data)
        
        if not data:
            return jsonify({"status": "error", "message": "Invalid JSON data"}), 400
            
        playlist_name = data.get("playlist_name", "Untitled Playlist")
        tracks = data.get("tracks", [])

        if not tracks:
            return jsonify({"status": "error", "message": "No tracks provided."}), 400

        from app.models import Playlist, PlaylistTrack  # local import to avoid top-level clutter

        # Create playlist
        playlist = Playlist(name=playlist_name, owner_id=current_user.id)
        db.session.add(playlist)
        db.session.flush()  # ensures playlist.id is available

        track_objects = []  # Keep track of created tracks for the response

        for song in tracks:
            title = song.get("name")
            artist = song.get("artist")
            duration = int(song.get("duration_ms", 0))

            if not title or not artist:
                continue

            # Check if track already exists
            track = Track.query.filter_by(title=title, artist=artist).first()
            if not track:
                try:
                    # Now we can include user_id directly in the constructor
                    track = Track(
                        title=title,
                        artist=artist,
                        genre=song.get("genre", "Unknown"),
                        tempo=float(song.get("tempo", 0)),
                        valence=float(song.get("valence", 0)),
                        energy=float(song.get("energy", 0)),
                        date_played=datetime.now(),
                        acousticness=float(song.get("acousticness", 0)),
                        liveness=float(song.get("liveness", 0)),
                        danceability=float(song.get("danceability", 0)),
                        mode=song.get("mode", "Major"),
                        user_id=current_user.id  # We can now include this directly
                    )
                    
                    db.session.add(track)
                    db.session.flush()
                except Exception as e:
                    print(f"Error creating track: {e}")
                    return jsonify({"status": "error", "message": f"Error creating track: {e}"}), 400

            # Add track to playlist
            db.session.add(PlaylistTrack(playlist_id=playlist.id, track_id=track.id))
            track_objects.append(track)

            # Add to user's listened tracks if not already there
            if not UserTrack.query.filter_by(user_id=current_user.id, track_id=track.id).first():
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
        
        return jsonify({
            "status": "success",
            "message": f"Playlist '{playlist_name}' created.",
            "playlist": {
                "name": playlist.name,
                "tracks": [
                    {
                        "title": t.title,
                        "artist": t.artist,
                        "genre": t.genre,
                        "valence": t.valence,
                        "energy": t.energy,
                        "acousticness": t.acousticness
                    } for t in track_objects
                ]
            }
        })
    
    except Exception as e:
        db.session.rollback()
        print(f"Exception in create_playlist: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400