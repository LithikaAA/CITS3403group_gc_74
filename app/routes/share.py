import os
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from ..models import db, User, Playlist, Share, SharedData, Track

share_bp = Blueprint('share', __name__, url_prefix='/share')

# ---------- File upload settings ----------
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'csv', 'json'}
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

#################################################
# Helpers
#################################################

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#################################################
# Route handlers
#################################################

# ---------- Share Playlist ----------
@share_bp.route('/', methods=['GET', 'POST'])
@login_required
def share():
    playlists = Playlist.query.filter_by(owner_id=current_user.id).all()
    friends = User.query.filter(User.id != current_user.id).all()

    if request.method == 'POST':
        playlist_ids = request.form.getlist('playlist_ids')
        friend_ids   = request.form.getlist('friend_ids')

        if not playlist_ids or not friend_ids:
            flash('Please select at least one playlist and one friend.', 'error')
            return redirect(url_for('share.share'))

        for friend_id in friend_ids:
            for playlist_id in playlist_ids:
                # avoid duplicate shares
                exists = Share.query.filter_by(
                    playlist_id=int(playlist_id),
                    recipient_id=int(friend_id),
                    owner_id=current_user.id
                ).first()
                if not exists:
                    new_share = Share(
                        playlist_id   = int(playlist_id),
                        recipient_id  = int(friend_id),
                        owner_id      = current_user.id
                    )
                    db.session.add(new_share)

        db.session.commit()
        flash(f'Shared {len(playlist_ids)} playlist(s) with {len(friend_ids)} friend(s)!', 'success')
        return redirect(url_for('share.share'))

    # on GET, fetch both sent and received shares for the template
    received_shares = Share.query.filter_by(recipient_id=current_user.id).all()
    sent_shares     = Share.query.filter_by(owner_id=current_user.id).all()

    return render_template(
        'share.html',
        playlists       = playlists,
        friends         = friends,
        received_shares = received_shares,
        sent_shares     = sent_shares
    )


# ---------- Upload Shared Data ----------
@share_bp.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_shared_data():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            new_shared_data = SharedData(
                user_id   = current_user.id,
                file_path = file_path,
                file_name = filename,
                file_type = filename.rsplit('.', 1)[1].lower()
            )
            db.session.add(new_shared_data)
            db.session.commit()
            flash('File uploaded successfully!')
            return redirect(url_for('share.upload_shared_data'))

    shared_data = SharedData.query.filter_by(user_id=current_user.id).all()
    return render_template('share_upload.html', shared_data=shared_data)


# ---------- Delete Shared File ----------
@share_bp.route('/upload/delete/<int:data_id>', methods=['POST'])
@login_required
def delete_shared_data(data_id):
    shared_data = SharedData.query.get_or_404(data_id)
    if shared_data.user_id != current_user.id:
        return "Unauthorized", 403

    if os.path.exists(shared_data.file_path):
        os.remove(shared_data.file_path)

    db.session.delete(shared_data)
    db.session.commit()
    flash('File deleted successfully!')
    return redirect(url_for('share.upload_shared_data'))


# ---------- View Shared Dashboard ----------
@share_bp.route('/shared')
@login_required
def shared_dashboard():
    """
    Display the shared dashboard with playlist comparison interface
    """
    # Get user playlists
    playlists = Playlist.query.filter_by(owner_id=current_user.id).all()
    
    # Get shared playlists
    shared_playlists = Share.query.filter_by(recipient_id=current_user.id).all()

    # If there are no shared playlists, show no-friends message
    if not shared_playlists:
        return render_template(
            'shared_dashboard.html',
            shared_playlists    = [],
            playlists           = playlists,
            shared_summary      = None,
            top_popular_songs   = {"you": [], "friend": []},
            comparison_minutes  = {"labels": [], "your_data": [], "friend_data": []},
            comparison_bubble   = {"you": [], "friend": []},
            comparison_mood     = {"you": [], "friend": []},
            comparison_mode     = {"you": [], "friend": []}
        )

    # Provide dummy placeholders until AJAX fills real data
    placeholder_summary = {
        "common_track": "N/A",
        "your_avg_tempo": 0,
        "friend_avg_tempo": 0,
        "your_total_minutes": 0,
        "friend_total_minutes": 0,
        "your_mood": "N/A",
        "friend_mood": "N/A"
    }

    return render_template(
        'shared_dashboard.html',
        playlists           = playlists,
        shared_playlists    = shared_playlists,
        shared_summary      = placeholder_summary,
        top_popular_songs   = {"you": [], "friend": []},
        comparison_minutes  = {"labels": [], "your_data": [], "friend_data": []},
        comparison_bubble   = {"you": [], "friend": []},
        comparison_mood     = {"you": [], "friend": []},
        comparison_mode     = {"you": [], "friend": []}
    )


@share_bp.route('/compare-playlists')
@login_required
def compare_playlists():
    """
    Enhanced endpoint for comparing two playlists (yours and a friend's)
    Returns JSON data for updating the charts based on the actual playlist data
    """
    your_id   = request.args.get('your_id', type=int)
    friend_id = request.args.get('friend_id', type=int)
    
    if not your_id or not friend_id:
        return jsonify({'error': 'Missing playlist IDs'}), 400
    
    # Get your playlist
    your_playlist = Playlist.query.get_or_404(your_id)
    if your_playlist.owner_id != current_user.id:
        return jsonify({'error': 'Unauthorized access to playlist'}), 403
    
    # Get friend's playlist
    friend_playlist = Playlist.query.get_or_404(friend_id)
    # Ensure it was shared with you
    share = Share.query.filter_by(
        playlist_id   = friend_id, 
        recipient_id  = current_user.id
    ).first()
    
    if not share:
        return jsonify({'error': 'Unauthorized access to friend playlist'}), 403
    
    # Validate playlists
    your_valid, your_message = validate_playlist(your_playlist)
    friend_valid, friend_message = validate_playlist(friend_playlist)
    
    if not your_valid:
        return jsonify({'error': f'Your playlist: {your_message}'}), 400
    
    if not friend_valid:
        return jsonify({'error': f'Friend playlist: {friend_message}'}), 400
    
    try:
        # Generate comparison data from the actual playlist content
        # Valence vs Acousticness chart data
        valence_acousticness = {
            'you': generate_valence_acousticness_data(your_playlist),
            'friend': generate_valence_acousticness_data(friend_playlist)
        }
        
        # Minutes by Track comparison data
        minutes_by_track = generate_minutes_by_track(your_playlist, friend_playlist)
        
        # Danceability vs Energy bubble chart data
        comparison_bubble = {
            'you': generate_bubble_data(your_playlist),
            'friend': generate_bubble_data(friend_playlist)
        }
        
        # Mood Profile radar chart data
        comparison_mood = {
            'you': generate_mood_data(your_playlist),
            'friend': generate_mood_data(friend_playlist)
        }
        
        # Mode (Major/Minor) comparison data
        comparison_mode = {
            'you': [count_by_mode(your_playlist, 1), count_by_mode(your_playlist, 0)],
            'friend': [count_by_mode(friend_playlist, 1), count_by_mode(friend_playlist, 0)]
        }
        
        # Calculate summary statistics
        summary = generate_summary(your_playlist, friend_playlist)
        
        # Get top popular songs
        top_popular_songs = {
            'you': get_top_popular_songs(your_playlist, 5),
            'friend': get_top_popular_songs(friend_playlist, 5)
        }
        
        print("Top songs you:", get_top_popular_songs(your_playlist, 5))
        print("Top songs friend:", get_top_popular_songs(friend_playlist, 5))

        # Get additional insights with the new helper functions
        similar_tracks = find_similar_tracks(your_playlist, friend_playlist, 'valence', 0.1)
        mood_difference = get_mood_difference(your_playlist, friend_playlist)
        comparative_stats = get_comparative_stats(your_playlist, friend_playlist)
        recommendations = generate_playlist_recommendations(your_playlist, friend_playlist)
        
        # Add annotations for the valence-acousticness chart
        chart_annotations = generate_quadrant_annotations()
        def safe_preview(obj):
            try:
                return obj[:1]
            except Exception as e:
                return f"Error previewing: {e}"

        print("valence_acousticness:", type(valence_acousticness), safe_preview(valence_acousticness))
        print("minutes_by_track:", type(minutes_by_track), safe_preview(minutes_by_track))
        print("comparison_bubble:", type(comparison_bubble), safe_preview(comparison_bubble))
        print("comparison_mood:", type(comparison_mood), safe_preview(comparison_mood))
        print("comparison_mode:", type(comparison_mode), safe_preview(comparison_mode))
        print("summary:", type(summary), safe_preview(summary))
        print("top_popular_songs:", type(top_popular_songs), safe_preview(top_popular_songs))
        print("chart_annotations:", type(chart_annotations), safe_preview(chart_annotations))
        print("similar_tracks:", type(similar_tracks), safe_preview(similar_tracks))
        print("mood_difference:", type(mood_difference), safe_preview(mood_difference))
        print("comparative_stats:", type(comparative_stats), safe_preview(comparative_stats))

        return jsonify({
            'valence_acousticness': valence_acousticness,
            'comparison_minutes': minutes_by_track,
            'comparison_bubble': comparison_bubble,
            'comparison_mood': comparison_mood,
            'comparison_mode': comparison_mode,
            'shared_summary': summary,
            'top_popular_songs': top_popular_songs,
            'chart_annotations': chart_annotations,
            'similar_tracks': [
                {
                    'your_track': t[0].to_dict() if t[0] else None,
                    'friend_track': t[1].to_dict() if t[1] else None,
                    'similarity': t[2]
                } for t in similar_tracks[:5]
            ]
            ,
            'mood_difference': mood_difference,
            'comparative_stats': comparative_stats,
            'recommendations': recommendations
        })
    
    except Exception as e:
        current_app.logger.error(f"Error generating comparison data: {str(e)}")
        return jsonify({'error': 'Error generating comparison data'}), 500

#################################################
# Data Validation and Error Handling
#################################################

def validate_playlist(playlist):
    """
    Validate if a playlist has tracks and required attributes
    Returns a tuple (is_valid, message)
    """
    if not playlist:
        return False, "Playlist not found"
    
    if not hasattr(playlist, 'tracks') or not playlist.tracks:
        return False, "Playlist has no tracks"
    
    return True, "Valid playlist"

def safe_get_attribute(track, attribute, default_value=0):
    """
    Safely get an attribute from a track with a default value
    Handles missing attributes and type conversion errors
    """
    try:
        value = getattr(track, attribute, default_value)
        # Try to convert to float for numerical attributes
        return float(value) if value is not None else default_value
    except (ValueError, TypeError):
        return default_value

def get_track_features_safe(track):
    """
    Get all audio features from a track with safe defaults
    Returns a dictionary of features
    """
    return {
        'danceability': safe_get_attribute(track, 'danceability', 0.5),
        'energy': safe_get_attribute(track, 'energy', 0.5),
        'acousticness': safe_get_attribute(track, 'acousticness', 0.5),
        'valence': safe_get_attribute(track, 'valence', 0.5),
        'liveness': safe_get_attribute(track, 'liveness', 0.5),
        'speechiness': safe_get_attribute(track, 'speechiness', 0.5),
        'instrumentalness': safe_get_attribute(track, 'instrumentalness', 0.5),
        'tempo': safe_get_attribute(track, 'tempo', 120),
        'duration_minutes': safe_get_attribute(track, 'duration_minutes', 3),
        'popularity': safe_get_attribute(track, 'popularity', 50),
        'mode': int(safe_get_attribute(track, 'mode', 1))  # Major = 1, Minor = 0
    }

#################################################
# Chart Data Generation
#################################################

def generate_valence_acousticness_data(playlist):
    """Generate data points for valence vs acousticness chart from actual tracks"""
    data = []
    for track in playlist.tracks:
        features = get_track_features_safe(track)
        data.append({
            'x': features['acousticness'],
            'y': features['valence'],
            'title': track.title,
            'artist': track.artist
        })
    return data

def generate_minutes_by_track(your_playlist, friend_playlist):
    """
    Generate minutes played comparison data for common tracks
    between your playlist and friend's playlist
    """
    # Get track info from both playlists
    your_tracks = {track.title: safe_get_attribute(track, 'duration_minutes', 3) 
                   for track in your_playlist.tracks}
    friend_tracks = {track.title: safe_get_attribute(track, 'duration_minutes', 3) 
                     for track in friend_playlist.tracks}
    
    # Find common tracks or all tracks if few in common
    common_tracks = set(your_tracks.keys()) & set(friend_tracks.keys())
    if len(common_tracks) < 3:
        # Use top tracks from each playlist if few common tracks
        your_top = sorted(your_tracks.items(), key=lambda x: x[1], reverse=True)[:3]
        friend_top = sorted(friend_tracks.items(), key=lambda x: x[1], reverse=True)[:3]
        track_titles = list(set([t[0] for t in your_top] + [t[0] for t in friend_top]))[:5]
    else:
        track_titles = list(common_tracks)[:5]
    
    # Create comparison data
    your_data = [your_tracks.get(title, 0) for title in track_titles]
    friend_data = [friend_tracks.get(title, 0) for title in track_titles]
    
    return {
        'labels': track_titles,
        'your_data': your_data,
        'friend_data': friend_data
    }

def generate_bubble_data(playlist):
    """Generate bubble chart data based on danceability, energy and duration"""
    data = []
    for track in playlist.tracks:
        features = get_track_features_safe(track)
        
        data.append({
            'x': features['danceability'],
            'y': features['energy'],
            'r': features['duration_minutes'] * 5,  # Scale minutes to radius
            'title': track.title,
            'artist': track.artist
        })
    return data

def generate_mood_data(playlist):
    """Generate mood profile data based on audio features"""
    # Calculate averages for each audio feature
    return [
        average_attribute(playlist, 'danceability'),
        average_attribute(playlist, 'energy'),
        average_attribute(playlist, 'valence'),
        average_attribute(playlist, 'acousticness'),
        average_attribute(playlist, 'liveness')
    ]

def average_attribute(playlist, attribute):
    """Calculate average value of an audio feature across all tracks"""
    values = [safe_get_attribute(track, attribute, 0) for track in playlist.tracks]
    return sum(values) / len(values) if values else 0.5

def count_by_mode(playlist, mode_value):
    """Count tracks with a specific mode (major=1, minor=0)"""
    return sum(1 for track in playlist.tracks if int(safe_get_attribute(track, 'mode', 1)) == mode_value)

def generate_summary(your_playlist, friend_playlist):
    """Generate summary statistics comparing two playlists"""
    # Find common tracks
    your_track_titles = set(track.title for track in your_playlist.tracks)
    friend_track_titles = set(track.title for track in friend_playlist.tracks)
    common_tracks = your_track_titles.intersection(friend_track_titles)
    
    # Find a common track or the first track from your playlist
    common_track = next(iter(common_tracks), "No common tracks")
    if common_track == "No common tracks" and your_playlist.tracks:
        common_track = your_playlist.tracks[0].title
    
    return {
        'common_track': common_track,
        'your_avg_tempo': calculate_avg_tempo(your_playlist),
        'friend_avg_tempo': calculate_avg_tempo(friend_playlist),
        'your_total_minutes': calculate_total_minutes(your_playlist),
        'friend_total_minutes': calculate_total_minutes(friend_playlist),
        'your_mood': determine_mood(your_playlist),
        'friend_mood': determine_mood(friend_playlist)
    }

def get_top_song(playlist):
    """Get the most played/longest song title"""
    if not playlist.tracks:
        return "No songs"
    
    # Sort by duration and return top
    tracks_sorted = sorted(playlist.tracks, 
                          key=lambda t: safe_get_attribute(t, 'duration_minutes', 0), 
                          reverse=True)
    return tracks_sorted[0].title if tracks_sorted else "No songs"

def calculate_total_minutes(playlist):
    """Calculate total minutes of all tracks"""
    return round(sum(safe_get_attribute(track, 'duration_minutes', 0) for track in playlist.tracks), 1)

def calculate_avg_tempo(playlist):
    """Calculate average tempo of all tracks"""
    tempos = [safe_get_attribute(track, 'tempo', 0) for track in playlist.tracks]
    return round(sum(tempos) / len(tempos), 1) if tempos else 0

def determine_mood(playlist):
    """Determine overall mood based on audio features"""
    valence = average_attribute(playlist, 'valence')
    energy = average_attribute(playlist, 'energy')
    
    if valence > 0.6 and energy > 0.6:
        return "Energetic"
    elif valence > 0.6 and energy <= 0.6:
        return "Happy"
    elif valence <= 0.4 and energy > 0.6:
        return "Angry"
    elif valence <= 0.4 and energy <= 0.4:
        return "Sad"
    else:
        return "Balanced"

def get_top_popular_songs(playlist, limit=5):
    """Get top popular songs from playlist based on popularity attribute"""
    if not playlist.tracks:
        return []
    
    # Sort by popularity and return top tracks
    tracks_sorted = sorted(playlist.tracks, 
                          key=lambda t: safe_get_attribute(t, 'popularity', 0), 
                          reverse=True)
    return [{'title': t.title, 'artist': t.artist} for t in tracks_sorted[:limit]]

#################################################
# Enhanced Analysis Functions
#################################################

def find_similar_tracks(your_playlist, friend_playlist, feature='valence', threshold=0.1):
    """
    Find tracks that are similar between two playlists based on a specific feature
    Returns list of tuples (your_track, friend_track, similarity_score)
    """
    similar_tracks = []
    
    for your_track in your_playlist.tracks:
        your_value = safe_get_attribute(your_track, feature)
        
        for friend_track in friend_playlist.tracks:
            friend_value = safe_get_attribute(friend_track, feature)
            
            # Calculate similarity (lower is more similar)
            similarity = abs(your_value - friend_value)
            
            if similarity <= threshold:
                similar_tracks.append((
                    your_track, 
                    friend_track, 
                    1.0 - similarity  # Convert to similarity score (higher is better)
                ))
    
    # Sort by similarity (highest first)
    return sorted(similar_tracks, key=lambda x: x[2], reverse=True)

def get_mood_difference(your_playlist, friend_playlist):
    """
    Calculate and explain mood differences between playlists
    Returns description of mood differences
    """
    your_valence = average_attribute(your_playlist, 'valence')
    your_energy = average_attribute(your_playlist, 'energy')
    friend_valence = average_attribute(friend_playlist, 'valence')
    friend_energy = average_attribute(friend_playlist, 'energy')
    
    valence_diff = your_valence - friend_valence
    energy_diff = your_energy - friend_energy
    
    # Generate mood difference explanation
    explanation = []
    
    if abs(valence_diff) > 0.15:
        if valence_diff > 0:
            explanation.append("Your music is more upbeat and positive than your friend's.")
        else:
            explanation.append("Your friend's music is more upbeat and positive than yours.")
    
    if abs(energy_diff) > 0.15:
        if energy_diff > 0:
            explanation.append("Your music has higher energy than your friend's.")
        else:
            explanation.append("Your friend's music has higher energy than yours.")
    
    if not explanation:
        explanation.append("You and your friend have similar mood preferences in music.")
    
    return " ".join(explanation)

def get_genre_statistics(playlist):
    """
    Analyze genres in the playlist
    Returns dict with genre counts and percentages
    """
    if not playlist.tracks:
        return {}
    
    genre_counts = {}
    total_tracks = len(playlist.tracks)
    
    for track in playlist.tracks:
        genres = getattr(track, 'genres', [])
        if not genres:
            continue
            
        for genre in genres:
            genre_counts[genre] = genre_counts.get(genre, 0) + 1
    
    # Calculate percentages
    genre_stats = {
        'counts': genre_counts,
        'percentages': {g: (c / total_tracks * 100) for g, c in genre_counts.items()},
        'top_genres': sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    }
    
    return genre_stats

def generate_playlist_recommendations(your_playlist, friend_playlist):
    """
    Generate recommendations based on playlist comparison
    Returns a list of recommendation objects
    """
    recommendations = []
    
    # Find tracks your friend might like based on your playlist
    your_top_tracks = sorted(
        your_playlist.tracks, 
        key=lambda t: safe_get_attribute(t, 'popularity', 0), 
        reverse=True
    )[:5]
    
    # Find your friend's mood
    friend_mood = determine_mood(friend_playlist)
    
    # Find tracks that match your friend's mood
    mood_matches = []
    for track in your_top_tracks:
        track_features = get_track_features_safe(track)
        track_mood = determine_track_mood(track_features)
        
        if track_mood == friend_mood:
            mood_matches.append(track)
    
    # Add recommendation for matching tracks
    if mood_matches:
        recommendations.append({
            'type': 'track_recommendation',
            'title': "Songs your friend might like",
            'description': f"...",
            'tracks': [t.to_dict() for t in mood_matches[:3]]  # ✅ JSON-safe
        })
    
    # Add recommendation based on musical difference
    mood_diff = get_mood_difference(your_playlist, friend_playlist)
    if mood_diff and not mood_diff.startswith("You and your friend have similar"):
        recommendations.append({
            'type': 'mood_insight',
            'title': "Music Mood Insight",
            'description': mood_diff
        })
    
    return recommendations

def determine_track_mood(track_features):
    """
    Determine the mood of a single track based on its features
    Returns mood classification
    """
    valence = track_features['valence']
    energy = track_features['energy']
    
    if valence > 0.6 and energy > 0.6:
        return "Energetic"
    elif valence > 0.6 and energy <= 0.6:
        return "Happy"
    elif valence <= 0.4 and energy > 0.6:
        return "Angry"
    elif valence <= 0.4 and energy <= 0.4:
        return "Sad"
    else:
        return "Balanced"

#################################################
# Visualization Enhancement Functions
#################################################

def generate_quadrant_annotations():
    """
    Generate annotations for quadrants in the valence-acousticness chart
    Returns annotation config for Chart.js
    """
    return {
        'annotations': {
            'quadrantLines': {
                'type': 'line',
                'xMin': 0.5,
                'xMax': 0.5,
                'yMin': 0,
                'yMax': 1,
                'borderColor': 'rgba(0, 0, 0, 0.1)',
                'borderWidth': 1,
                'borderDash': [5, 5]
            },
            'horizontalCenter': {
                'type': 'line',
                'yMin': 0.5,
                'yMax': 0.5,
                'xMin': 0,
                'xMax': 1,
                'borderColor': 'rgba(0, 0, 0, 0.1)',
                'borderWidth': 1,
                'borderDash': [5, 5]
            },
            'quadrantLabels': [
                {
                    'type': 'label',
                    'xValue': 0.25,
                    'yValue': 0.75,
                    'content': 'Happy & Electronic',
                    'backgroundColor': 'rgba(99, 102, 241, 0.1)',
                    'color': '#6366F1'
                },
                {
                    'type': 'label',
                    'xValue': 0.75,
                    'yValue': 0.75,
                    'content': 'Uplifting & Acoustic',
                    'backgroundColor': 'rgba(99, 102, 241, 0.1)',
                    'color': '#6366F1'
                },
                {
                    'type': 'label',
                    'xValue': 0.25,
                    'yValue': 0.25,
                    'content': 'Sad & Electronic',
                    'backgroundColor': 'rgba(244, 114, 182, 0.1)',
                    'color': '#F472B6'
                },
                {
                    'type': 'label',
                    'xValue': 0.75,
                    'yValue': 0.25,
                    'content': 'Mellow & Acoustic',
                    'backgroundColor': 'rgba(244, 114, 182, 0.1)',
                    'color': '#F472B6'
                }
            ]
        }
    }

def get_comparative_stats(your_playlist, friend_playlist):
    """
    Get statistical comparison between playlists
    Returns dict with statistical insights
    """
    stats = {}
    
    # Compare tempo
    your_tempo = calculate_avg_tempo(your_playlist)
    friend_tempo = calculate_avg_tempo(friend_playlist)
    tempo_diff = abs(your_tempo - friend_tempo)
    tempo_percent = (tempo_diff / max(your_tempo, friend_tempo)) * 100 if max(your_tempo, friend_tempo) > 0 else 0
    
    stats['tempo'] = {
        'your_tempo': your_tempo,
        'friend_tempo': friend_tempo,
        'difference': tempo_diff,
        'percent_difference': tempo_percent,
        'description': f"Your music is on average {'faster' if your_tempo > friend_tempo else 'slower'} by {tempo_diff:.1f} BPM ({tempo_percent:.1f}%)"
    }
    
    # Compare total duration
    your_duration = calculate_total_minutes(your_playlist)
    friend_duration = calculate_total_minutes(friend_playlist)
    duration_diff = abs(your_duration - friend_duration)
    
    stats['duration'] = {
        'your_duration': your_duration,
        'friend_duration': friend_duration,
        'difference': duration_diff,
        'description': f"You have {'more' if your_duration > friend_duration else 'less'} total listening time by {duration_diff:.1f} minutes"
    }
    
    # Compare mood profiles
    your_mood_data = generate_mood_data(your_playlist)
    friend_mood_data = generate_mood_data(friend_playlist)
    
    # Calculate average difference across mood dimensions
    mood_diffs = [abs(yours - friends) for yours, friends in zip(your_mood_data, friend_mood_data)]
    avg_mood_diff = sum(mood_diffs) / len(mood_diffs) if mood_diffs else 0
    
    # Interpret similarity
    similarity_desc = ""
    if avg_mood_diff < 0.1:
        similarity_desc = "Your musical tastes are very similar!"
    elif avg_mood_diff < 0.2:
        similarity_desc = "You have moderately similar music preferences."
    else:
        similarity_desc = "Your musical tastes are quite different."
    
    stats['mood_similarity'] = {
        'average_difference': avg_mood_diff,
        'description': similarity_desc,
        'details': mood_diffs
    }
    
    return stats
