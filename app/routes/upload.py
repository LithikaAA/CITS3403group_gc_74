import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, session

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
