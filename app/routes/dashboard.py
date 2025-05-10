from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from app.models import db, User, Playlist, Track
from flask_login import current_user, login_required
from sqlalchemy import func
import pandas as pd
from collections import Counter

# Blueprint declaration
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    # Ensure user session
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    # Fetch user playlists
    playlists = Playlist.query.filter_by(owner_id=current_user.id).all()

    # Default placeholder data
    default_data = {
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

    # No playlists: render empty dashboard
    if not playlists:
        flash("You don't have any playlists yet. Create one to get started!", "info")
        return render_template(
            'dashboard.html',
            playlists=[],
            has_playlists=False,
            selected_playlist=None,
            valence_acousticness=default_data['valence_acousticness'],
            danceability_energy=default_data['danceability_energy'],
            mood_profile=default_data['mood_profile'],
            mode=default_data['mode'],
            mode_count=default_data['mode_count'],
            top_summary=default_data['top_summary'],
            top_popular_songs=default_data['top_popular_songs'],
            major=0,
            minor=0
        )

    # Determine selected playlist
    playlist_id = request.args.get('playlist_id', type=int)
    if playlist_id:
        selected = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
        selected_playlist = selected if selected else playlists[0]
    else:
        selected_playlist = playlists[0]

    # Compile stats
    data = get_playlist_statistics(selected_playlist)

    return render_template(
        'dashboard.html',
        playlists=playlists,
        has_playlists=True,
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

@dashboard_bp.route('/playlist/create', methods=['GET', 'POST'])
@login_required
def create_playlist():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description', '')
        if not name:
            flash('Please provide a name for your playlist.', 'error')
            return redirect(url_for('dashboard.dashboard'))
        new_playlist = Playlist(name=name, description=description, owner_id=current_user.id)
        db.session.add(new_playlist)
        db.session.commit()
        flash(f'Playlist "{name}" created successfully!', 'success')
        return redirect(url_for('dashboard.dashboard', playlist_id=new_playlist.id))
    return render_template('create_playlist.html')

@dashboard_bp.route('/playlist/<int:playlist_id>/delete', methods=['POST'])
@login_required
def delete_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    if not playlist:
        flash('Playlist not found.', 'error')
        return redirect(url_for('dashboard.dashboard'))
    name = playlist.name
    db.session.delete(playlist)
    db.session.commit()
    flash(f'Playlist "{name}" deleted successfully.', 'success')
    return redirect(url_for('dashboard.dashboard'))

@dashboard_bp.route('/playlist/<int:playlist_id>/add-track', methods=['POST'])
@login_required
def add_track_to_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    track = Track.query.get(request.form.get('track_id'))
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
    track = Track.query.get(request.form.get('track_id'))
    if track and track in playlist.tracks:
        playlist.tracks.remove(track)
        db.session.commit()
    return jsonify({"success": "Track removed from playlist"})

@dashboard_bp.route('/search-tracks')
@login_required
def search_tracks():
    q = request.args.get('q', '')
    if len(q) < 2:
        return jsonify({"tracks": []})
    tracks = Track.query.filter(
        (Track.title.ilike(f'%{q}%')) | (Track.artist.ilike(f'%{q}%'))
    ).limit(10).all()
    return jsonify({"tracks": [
        {'id': t.id, 'title': t.title, 'artist': t.artist, 'album': t.album} for t in tracks
    ]})

@dashboard_bp.route('/export-playlist/<int:playlist_id>')
@login_required
def export_playlist(playlist_id):
    playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
    if not playlist:
        return jsonify({"error": "Playlist not found"}), 404
    data = [{
        'title': t.title, 'artist': t.artist, 'album': t.album,
        'danceability': t.danceability, 'energy': t.energy,
        'valence': t.valence, 'tempo': t.tempo
    } for t in playlist.tracks]
    df = pd.DataFrame(data)
    csv_data = df.to_csv(index=False)
    return jsonify({"data": csv_data, "filename": f"{playlist.name}_export.csv"})


def get_playlist_statistics(playlist):
    """
    Compile various statistics for the given playlist.
    """
    if not playlist or not playlist.tracks:
        return {
            'valence_acousticness': {'data': []},
            'danceability_energy': {'data': []},
            'mood_profile': {'data': [0, 0, 0, 0, 0]},
            'mode': {'data': [0, 0]},
            'mode_count': {'data': [0, 0]},
            'top_summary': {'most_played': 'No tracks yet', 'total_minutes': 0, 'avg_tempo': 0},
            'top_popular_songs': []
        }
    tracks = playlist.tracks
    # Valence vs Acousticness
    valence_acousticness = [
        {'x': round(t.acousticness or 0, 3), 'y': round(t.valence or 0, 3), 'title': t.title, 'artist': t.artist}
        for t in tracks if t.valence is not None and t.acousticness is not None
    ]
    # Danceability vs Energy
    danceability_energy = [
        {'x': round(t.danceability or 0, 2), 'y': round(t.energy or 0, 2), 'r': 20, 'title': t.title, 'artist': t.artist}
        for t in tracks if t.danceability is not None and t.energy is not None
    ]
    # Mood profile averages
    attrs = ["danceability", "energy", "valence", "acousticness", "liveness"]
    mood_profile = [
        round(sum(getattr(t, a, 0) or 0 for t in tracks) / len(tracks), 2) for a in attrs
    ]
    # Mode counts
    major = sum(str(t.mode).lower() == "major" for t in tracks)
    minor = sum(str(t.mode).lower() == "minor" for t in tracks)
    # Top popular songs
    top_pop = sorted(tracks, key=lambda t: getattr(t, 'popularity', 0), reverse=True)[:5]
    top_popular_songs = [{'title': t.title, 'artist': t.artist, 'popularity': getattr(t, 'popularity', 0)} for t in top_pop]
    # Duration & tempo
    durations = [t.duration_ms for t in tracks if t.duration_ms]
    avg_dur = sum(durations) / len(durations) if durations else 210000
    total_mins = round(len(tracks) * avg_dur / 60000, 1)
    tempos = [t.tempo for t in tracks if t.tempo is not None]
    avg_tempo = round(sum(tempos) / len(tempos), 1) if tempos else 0
    # Summary
    top_duration = max(tracks, key=lambda t: getattr(t, 'duration_ms', 0), default=None)
    return {
        'valence_acousticness': {'data': valence_acousticness},
        'danceability_energy': {'data': danceability_energy},
        'mood_profile': {'data': mood_profile},
        'mode': {'data': [major, minor]},
        'mode_count': {'data': [major, minor]},
        'top_summary': {'most_played': top_duration.title if top_duration else 'No tracks yet', 'total_minutes': total_mins, 'avg_tempo': avg_tempo},
        'top_popular_songs': top_popular_songs
    }