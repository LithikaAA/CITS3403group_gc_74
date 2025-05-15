import os
import traceback
from flask import (
    Blueprint, render_template, request, session, jsonify, current_app
)
from flask_login import current_user, login_required
from flask_wtf.csrf import generate_csrf
from app.models import db, Track, UserTrack, Playlist, PlaylistTrack
from app.utils.spotify_auth import search_tracks
from app.utils.track_feature_loader import get_track_features_by_id

# Enable detailed debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

upload_bp = Blueprint('upload', __name__)

# ---------- Main Upload Page ----------
@upload_bp.route('/upload', methods=['GET'])
@login_required
def upload():
    username = session.get('username', 'User')
    song_count = UserTrack.query.filter_by(user_id=current_user.id).count() if current_user.is_authenticated else 0
    # Generate CSRF token and add it to the template
    csrf_token = generate_csrf()
    playlists = Playlist.query.filter_by(owner_id=current_user.id).all()
    return render_template('upload.html', username=username, song_count=song_count, csrf_token_value=csrf_token, playlists=playlists)


# ---------- Search Songs (Spotify API + CSV metadata) ----------
@upload_bp.route("/api/search-tracks")
@login_required
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
@login_required
def create_playlist():
    try:
        logger.debug("Starting playlist creation process")
        
        # Validate request data
        data = request.get_json()
        if not data:
            logger.warning("No JSON data provided in request")
            return jsonify({"status": "error", "message": "No data provided"}), 400
            
        playlist_name = data.get("playlist_name", "Untitled Playlist")
        tracks = data.get("tracks", [])

        if not tracks:
            logger.warning("No tracks provided in request")
            return jsonify({"status": "error", "message": "No tracks provided."}), 400

        # Log data for debugging
        logger.debug(f"Playlist name: {playlist_name}")
        logger.debug(f"Number of tracks: {len(tracks)}")
        
        # Import here to avoid circular dependency
        from app.models import Playlist, PlaylistTrack  
        
        try:
            # Create playlist record
            playlist = Playlist(
                name=playlist_name, 
                owner_id=current_user.id
            )
            db.session.add(playlist)
            db.session.flush()  # Ensures playlist.id is generated
            logger.debug(f"Created playlist with ID: {playlist.id}")

            # Add tracks to playlist
            for index, song in enumerate(tracks):
                # Handle the different key naming in frontend and backend
                title = song.get("title") or song.get("name")
                artist = song.get("artist")
                
                # Basic validation
                if not title or not artist:
                    logger.warning(f"Skipping track at index {index} - missing title or artist")
                    continue

                # Convert string values to appropriate types
                try:
                    duration = int(song.get("duration_ms", 0))
                    tempo = float(song.get("tempo")) if song.get("tempo") is not None else None
                    danceability = float(song.get("danceability")) if song.get("danceability") is not None else None
                    energy = float(song.get("energy")) if song.get("energy") is not None else None
                    liveness = float(song.get("liveness")) if song.get("liveness") is not None else None
                    acousticness = float(song.get("acousticness")) if song.get("acousticness") is not None else None
                    valence = float(song.get("valence")) if song.get("valence") is not None else None
                except (ValueError, TypeError) as e:
                    logger.warning(f"Type conversion error for track {title}: {str(e)}")
                    # Use default values instead of failing
                    duration = 0
                    tempo = None
                    danceability = None
                    energy = None
                    liveness = None
                    acousticness = None
                    valence = None
                
                # Get or create track
                track = Track.query.filter_by(title=title, artist=artist).first()
                if not track:
                    logger.debug(f"Creating new track: {title} by {artist}")
                    track = Track(
                        title=title,
                        artist=artist,
                        genre=song.get("genre"),
                        tempo=tempo,
                        valence=valence,
                        energy=energy,
                        acousticness=acousticness,
                        liveness=liveness,
                        danceability=danceability,
                        mode=song.get("mode"),
                        duration_ms=duration,  # Adding the duration_ms field
                        user_id=current_user.id
                    )
                    db.session.add(track)
                    db.session.flush()

                # Create playlist-track relationship
                db.session.add(PlaylistTrack(playlist_id=playlist.id, track_id=track.id))
                logger.debug(f"Added track {track.id} to playlist {playlist.id}")

                # Add to user tracks if not already there
                user_track = UserTrack.query.filter_by(user_id=current_user.id, track_id=track.id).first()
                if not user_track:
                    logger.debug(f"Adding track {track.id} to user {current_user.id}'s collection")
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

            # Commit all changes
            db.session.commit()
            logger.info(f"Successfully created playlist '{playlist_name}' with {len(tracks)} tracks")
            
            # Return success response with playlist data
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
                        } for t in playlist.tracks
                    ]
                }
            })
            
        except Exception as db_error:
            # Roll back transaction on error
            db.session.rollback()
            error_traceback = traceback.format_exc()
            logger.error(f"Database error during playlist creation: {str(db_error)}")
            logger.error(error_traceback)
            return jsonify({
                "status": "error", 
                "message": f"Database error: {str(db_error)}"
            }), 500
            
    except Exception as e:
        # Catch any other exceptions
        error_traceback = traceback.format_exc()
        logger.error(f"Unexpected error during playlist creation: {str(e)}")
        logger.error(error_traceback)
        return jsonify({
            "status": "error", 
            "message": f"Server error: {str(e)}"
        }), 500

# ---------- Get Playlist Details ----------
@upload_bp.route("/api/playlist/<int:playlist_id>", methods=["GET"])
@login_required
def get_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    
    if not playlist:
        return jsonify({"status": "error", "message": "Playlist not found"}), 404
    
    tracks = []
    for pt in PlaylistTrack.query.filter_by(playlist_id=playlist.id).all():
        track = Track.query.get(pt.track_id)
        if track:
            tracks.append({
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "genre": track.genre,
                "danceability": track.danceability,
                "energy": track.energy,
                "liveness": track.liveness,
                "acousticness": track.acousticness,
                "valence": track.valence,
                "tempo": track.tempo,
                "mode": track.mode,
                "duration_ms": track.duration_ms
            })
    
    return jsonify({
        "status": "success",
        "playlist": {
            "id": playlist.id,
            "name": playlist.name,
            "tracks": tracks
        }
    })

# ---------- Add Track to Playlist ----------
@upload_bp.route("/api/playlist/<int:playlist_id>/add-track", methods=["POST"])
@login_required
def add_track_to_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    
    if not playlist:
        return jsonify({"status": "error", "message": "Playlist not found"}), 404
    
    data = request.get_json()
    track_id = data.get("track_id")
    
    if not track_id:
        # Extract track data and create a new track
        title = data.get("title")
        artist = data.get("artist")
        
        if not title or not artist:
            return jsonify({"status": "error", "message": "Track title and artist required"}), 400
        
        # Check if track exists
        track = Track.query.filter_by(title=title, artist=artist).first()
        
        if not track:
            # Create new track with all available data
            try:
                duration = int(data.get("duration_ms", 0))
                tempo = float(data.get("tempo")) if data.get("tempo") else None
                danceability = float(data.get("danceability")) if data.get("danceability") else None
                energy = float(data.get("energy")) if data.get("energy") else None
                liveness = float(data.get("liveness")) if data.get("liveness") else None
                acousticness = float(data.get("acousticness")) if data.get("acousticness") else None
                valence = float(data.get("valence")) if data.get("valence") else None
            except (ValueError, TypeError):
                duration = 0
                tempo = None
                danceability = None
                energy = None
                liveness = None
                acousticness = None
                valence = None
                
            track = Track(
                title=title,
                artist=artist,
                genre=data.get("genre"),
                tempo=tempo,
                valence=valence,
                energy=energy,
                acousticness=acousticness,
                liveness=liveness,
                danceability=danceability,
                mode=data.get("mode"),
                duration_ms=duration,
                user_id=current_user.id
            )
            db.session.add(track)
            db.session.flush()
        
        track_id = track.id
    
    # Check if track is already in playlist
    existing = PlaylistTrack.query.filter_by(playlist_id=playlist_id, track_id=track_id).first()
    if existing:
        return jsonify({"status": "error", "message": "Track already in playlist"}), 400
    
    # Add track to playlist
    playlist_track = PlaylistTrack(playlist_id=playlist_id, track_id=track_id)
    db.session.add(playlist_track)
    
    # Add to user tracks if not already there
    user_track = UserTrack.query.filter_by(user_id=current_user.id, track_id=track_id).first()
    if not user_track:
        track = Track.query.get(track_id)
        user_track = UserTrack(
            user_id=current_user.id,
            track_id=track_id,
            song=track.title,
            artist=track.artist,
            song_duration=track.duration_ms,
            times_played=1,
            total_ms_listened=track.duration_ms
        )
        db.session.add(user_track)
    
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Track added to playlist"})

# ---------- Remove Track from Playlist ----------
@upload_bp.route("/api/playlist/<int:playlist_id>/remove-track/<int:track_id>", methods=["DELETE"])
@login_required
def remove_track_from_playlist(playlist_id, track_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    
    if not playlist:
        return jsonify({"status": "error", "message": "Playlist not found"}), 404
    
    playlist_track = PlaylistTrack.query.filter_by(playlist_id=playlist_id, track_id=track_id).first()
    
    if not playlist_track:
        return jsonify({"status": "error", "message": "Track not in playlist"}), 404
    
    db.session.delete(playlist_track)
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Track removed from playlist"})

# ---------- Update Playlist ----------
@upload_bp.route("/api/playlist/<int:playlist_id>", methods=["POST"])
@login_required
def update_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    
    if not playlist:
        return jsonify({"status": "error", "message": "Playlist not found"}), 404
    
    data = request.get_json()
    new_name = data.get("name")
    
    if new_name:
        playlist.name = new_name
        db.session.commit()
    
    return jsonify({
        "status": "success",
        "message": "Playlist updated",
        "playlist": {
            "id": playlist.id,
            "name": playlist.name
        }
    })

# ---------- Delete Playlist ----------
@upload_bp.route("/api/playlist/<int:playlist_id>", methods=["DELETE"])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    
    if not playlist:
        return jsonify({"status": "error", "message": "Playlist not found"}), 404
    
    # Remove all playlist tracks
    PlaylistTrack.query.filter_by(playlist_id=playlist_id).delete()
    
    # Remove playlist
    db.session.delete(playlist)
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Playlist deleted"})


@upload_bp.route("/api/playlists", methods=["GET"])
@login_required
def get_playlists():
    playlists = Playlist.query.filter_by(owner_id=current_user.id).all()
    return jsonify({
        "status": "success",
        "playlists": [
            {
                "id": playlist.id,
                "name": playlist.name
            } for playlist in playlists
        ]
    })