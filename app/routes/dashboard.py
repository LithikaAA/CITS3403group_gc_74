from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify, flash
from app.models import db, User, Playlist, Track
from flask_login import current_user, login_required
from sqlalchemy import func
import pandas as pd
from collections import Counter

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
@login_required
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    playlists = Playlist.query.filter_by(owner_id=current_user.id).all()

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

    playlist_id = request.args.get('playlist_id', type=int)

    if playlist_id:
        selected_playlist = Playlist.query.filter_by(id=playlist_id, owner_id=current_user.id).first()
        if not selected_playlist:
            selected_playlist = playlists[0]
    else:
        selected_playlist = playlists[0]

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

    valence_acousticness_data = [
        {
            'x': round(t.acousticness or 0, 3),
            'y': round(t.valence or 0, 3),
            'title': t.title,
            'artist': t.artist
        }
        for t in tracks if t.valence is not None and t.acousticness is not None
    ]

    danceability_energy_data = [
        {
            'x': round(t.danceability or 0, 2),
            'y': round(t.energy or 0, 2),
            'r': 20,
            'title': t.title,
            'artist': t.artist
        }
        for t in tracks if t.danceability is not None and t.energy is not None
    ]

    mood_attributes = ["danceability", "energy", "valence", "acousticness", "liveness"]
    mood_profile_data = []
    for attr in mood_attributes:
        values = [getattr(t, attr, 0) or 0 for t in tracks]
        avg_value = round(sum(values) / len(values), 2) if values else 0
        mood_profile_data.append(avg_value)

    major_count = sum(1 for t in tracks if str(t.mode).lower() == "major")
    minor_count = sum(1 for t in tracks if str(t.mode).lower() == "minor")
    mode_count = {'data': [major_count, minor_count]}
    mode = {'data': [major_count, minor_count]}

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

    top_duration_song = max(tracks, key=lambda t: getattr(t, 'duration_ms', 0), default=None)
    top_duration_title = top_duration_song.title if top_duration_song else 'No tracks yet'

    durations = [getattr(t, 'duration_ms', 0) for t in tracks if getattr(t, 'duration_ms', 0) > 0]
    avg_duration_ms = sum(durations) / len(durations) if durations else 210000
    total_minutes = len(tracks) * avg_duration_ms / 60000

    tempo_values = [t.tempo for t in tracks if t.tempo is not None]
    avg_tempo = round(sum(tempo_values) / len(tempo_values), 1) if tempo_values else 0

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
