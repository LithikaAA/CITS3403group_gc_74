from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from app.models import db, User, Playlist, Track
from flask_login import current_user, login_required
from sqlalchemy import func
import pandas as pd
from collections import Counter

# Blueprint - notice the url_prefix parameter when registering the blueprint
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    playlists = Playlist.query.filter_by(owner_id=current_user.id).all()
    if not playlists:
        return render_template(
            'dashboard.html',
            playlists=[],
            valence_acousticness={'data': []},
            danceability_energy={'data': []},
            mood_profile={'data': [0, 0, 0, 0, 0]},
            mode={'data': [0, 0]},
            mode_count={'data': [0, 0]},
            top_summary={
                'most_played': 'No tracks yet',
                'total_minutes': 0,
                'avg_tempo': 0
            },
            top_popular_songs=[],
            major=0,
            minor=0
        )

    playlist_id = request.args.get('playlist_id', type=int)
    selected_playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first() if playlist_id else playlists[0]
    data = get_playlist_statistics(selected_playlist)
    return render_template(
        'dashboard.html',
        playlists=playlists,
        selected_playlist=selected_playlist,
        valence_acousticness=data['valence_acousticness'],
        danceability_energy=data['danceability_energy'],
        mood_profile=data['mood_profile'],
        mode=data['mode'],
        mode_count=data['mode_count'],
        top_summary=data['top_summary'],
        top_popular_songs=data['top_popular_songs'],
        major=data['mode_count']['data'][0],
        minor=data['mode_count']['data'][1]
    )

# Notice the route is now just '/playlist-data' since we have the url_prefix
@dashboard_bp.route('/playlist-data')
@login_required
def get_playlist_data():
    playlist_id = request.args.get('playlist_id', type=int)
    if not playlist_id:
        return jsonify({"error": "No playlist ID provided"}), 400
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    data = get_playlist_statistics(playlist)
    return jsonify(data)

def get_playlist_statistics(playlist):
    if not playlist or not playlist.tracks:
        return {
            'valence_acousticness': {'data': []},
            'danceability_energy': {'data': []},
            'mood_profile': {'data': [0, 0, 0, 0, 0]},
            'mode': {'data': [0, 0]},
            'mode_count': {'data': [0, 0]},
            'top_summary': {
                'most_played': 'No tracks yet',
                'total_minutes': 0,
                'avg_tempo': 0
            },
            'top_popular_songs': []
        }
    tracks = playlist.tracks
    # Valence vs Acousticness scatter data
    valence_acousticness_data = [
        {
            'x': round(t.acousticness or 0, 3),
            'y': round(t.valence or 0, 3),
            'title': t.title,
            'artist': t.artist
        }
        for t in tracks if t.valence is not None and t.acousticness is not None
    ]
    # Danceability vs Energy bubble chart
    danceability_energy_data = [
        {
            'x': round(t.danceability or 0, 2),
            'y': round(t.energy or 0, 2),
            'r': 20,  # fixed radius for now
            'title': t.title,
            'artist': t.artist
        }
        for t in tracks if t.danceability is not None and t.energy is not None
    ]
    # Mood Profile radar chart
    mood_attributes = ["danceability", "energy", "valence", "acousticness", "liveness"]
    mood_profile_data = []
    for attr in mood_attributes:
        values = [getattr(t, attr, 0) or 0 for t in tracks]
        avg_value = round(sum(values) / len(values), 2) if values else 0
        mood_profile_data.append(avg_value)
    # Mode Analysis (Major vs Minor) - count of songs (string-based)
    major_count = sum(1 for t in tracks if str(t.mode).lower() == "major")
    minor_count = sum(1 for t in tracks if str(t.mode).lower() == "minor")
    mode_count = {'data': [major_count, minor_count]}
    mode = {'data': [major_count, minor_count]}
    # Top 5 popular songs (by popularity, fallback to 0 if not present)
    top_popular_songs = sorted(
        tracks,
        key=lambda t: getattr(t, 'popularity', 0),
        reverse=True
    )[:5]
    top_popular_songs = [
        {
            'title': t.title,
            'artist': t.artist,
            'popularity': getattr(t, 'popularity', 0)
        }
        for t in top_popular_songs
    ]
    # Top duration songs (by duration_ms)
    top_duration_song = max(tracks, key=lambda t: getattr(t, 'duration_ms', 0), default=None)
    top_duration_title = top_duration_song.title if top_duration_song else 'No tracks yet'
    # Total minutes played (number of songs * average duration in ms)
    durations = [getattr(t, 'duration_ms', 0) for t in tracks if getattr(t, 'duration_ms', 0) > 0]
    if durations:
        avg_duration_ms = sum(durations) / len(durations)
    else:
        avg_duration_ms = 210000  # fallback to 3.5 min in ms if no data
    total_minutes = len(tracks) * avg_duration_ms / 60000
    # Average tempo
    tempo_values = [t.tempo for t in tracks if t.tempo is not None]
    avg_tempo = round(sum(tempo_values) / len(tempo_values), 1) if tempo_values else 0
    # Summary data
    top_summary = {
        'most_played': top_duration_title,
        'total_minutes': round(total_minutes, 1),
        'avg_tempo': avg_tempo
    }
    return {
        'valence_acousticness': {'data': valence_acousticness_data},
        'danceability_energy': {'data': danceability_energy_data},
        'mood_profile': {'data': mood_profile_data},
        'mode': mode,
        'mode_count': mode_count,
        'top_summary': top_summary,
        'top_popular_songs': top_popular_songs
    }

# All other routes adjusted for url_prefix
@dashboard_bp.route('/playlist/create', methods=['GET', 'POST'])
@login_required
def create_playlist():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        
        if not name:
            # Flash message would go here
            return redirect(url_for('dashboard.dashboard'))
        
        new_playlist = Playlist(
            name=name,
            description=description,
            owner_id=current_user.id
        )
        
        db.session.add(new_playlist)
        db.session.commit()
        
        return redirect(url_for('dashboard.dashboard', playlist_id=new_playlist.id))
    
    return render_template('create_playlist.html')

@dashboard_bp.route('/playlist/<int:playlist_id>/delete', methods=['POST'])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    
    if not playlist:
        # Flash message would go here
        return redirect(url_for('dashboard.dashboard'))
    
    db.session.delete(playlist)
    db.session.commit()
    
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/playlist/<int:playlist_id>/add-track', methods=['POST'])
@login_required
def add_track_to_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    
    track_id = request.form.get('track_id')
    track = Track.query.get(track_id)
    
    if not track:
        return jsonify({"error": "Track not found"}), 404
    
    playlist.tracks.append(track)
    db.session.commit()
    
    return jsonify({"success": "Track added to playlist"})

@dashboard_bp.route('/playlist/<int:playlist_id>/remove-track', methods=['POST'])
@login_required
def remove_track_from_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    
    track_id = request.form.get('track_id')
    track = Track.query.get(track_id)
    
    if not track:
        return jsonify({"error": "Track not found"}), 404
    
    if track in playlist.tracks:
        playlist.tracks.remove(track)
        db.session.commit()
    
    return jsonify({"success": "Track removed from playlist"})

@dashboard_bp.route('/search-tracks')
@login_required
def search_tracks():
    query = request.args.get('q', '')
    
    if not query or len(query) < 2:
        return jsonify({"tracks": []})
    
    # Search tracks by title or artist
    tracks = Track.query.filter(
        (Track.title.ilike(f'%{query}%')) | 
        (Track.artist.ilike(f'%{query}%'))
    ).limit(10).all()
    
    result = [
        {
            'id': track.id,
            'title': track.title,
            'artist': track.artist,
            'album': track.album
        } for track in tracks
    ]
    
    return jsonify({"tracks": result})

@dashboard_bp.route('/export-playlist/<int:playlist_id>')
@login_required
def export_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    
    # Create CSV data
    data = []
    for track in playlist.tracks:
        data.append({
            'title': track.title,
            'artist': track.artist,
            'album': track.album,
            'danceability': track.danceability,
            'energy': track.energy,
            'valence': track.valence,
            'tempo': track.tempo
        })
    
    df = pd.DataFrame(data)
    
    # Generate CSV
    csv_data = df.to_csv(index=False)
    
    response = jsonify({
        "data": csv_data,
        "filename": f"{playlist.name}_export.csv"
    })
    
    return response

# Add this code to your app.py or wherever you setup your Flask app
def register_blueprints(app):
    app.register_blueprint(dashboard_bp)
    # Register other blueprints as needed