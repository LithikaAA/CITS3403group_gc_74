import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session, jsonify
from app.models import Artist, Track, Playlist, db

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
@upload_bp.route('/upload/upload-csv', methods=['POST'])
def upload_csv():
    """
    Handle CSV playlist uploads.
    """
    file = request.files.get('playlist_csv')

    if not file or file.filename == '':
        flash(' No file selected. Please choose a CSV file.', 'error')
        return redirect(url_for('upload.upload'))

    # Define upload path
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)

    # Save the file safely
    file_path = os.path.join(upload_folder, file.filename)
    file.save(file_path)

    flash(f' Successfully uploaded "{file.filename}"!', 'success')
    return redirect(url_for('upload.upload'))


@upload_bp.route('/upload/new-playlist', methods=['GET', 'POST'])
def new_playlist():
    artists = Artist.query.order_by(Artist.name).all()
    selected_artist_id = request.form.get('artist')
    songs = []
    if selected_artist_id:
        songs = Track.query.join(Track.artists).filter(Artist.id == selected_artist_id).all()
    if request.method == 'POST' and request.form.get('song'):
        # Create the playlist
        playlist_name = request.form.get('playlist_name')
        song_id = request.form.get('song')
        user_id = session.get('user_id')
        playlist = Playlist(name=playlist_name, owner_id=user_id)
        db.session.add(playlist)
        db.session.commit()
        # Optionally add the song to the playlist here
        flash('Playlist created!', 'success')
        return redirect(url_for('upload.upload'))
    return render_template('new_playlist.html', artists=artists, songs=songs, selected_artist_id=selected_artist_id)


@upload_bp.route('/api/songs_by_artist/<int:artist_id>')
def songs_by_artist(artist_id):
    songs = Track.query.join(Track.artists).filter(Artist.id == artist_id).all()
    return jsonify([{'id': s.id, 'track_name': s.track_name} for s in songs])


