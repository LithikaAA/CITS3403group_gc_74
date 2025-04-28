from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from ..models import db, SharedVisualisation, SharedData
import os

from flask import Blueprint, render_template, request, redirect, url_for, flash


share_bp = Blueprint('share', __name__)

# Directory to store uploaded files
UPLOAD_FOLDER = 'app/static/uploads'
ALLOWED_EXTENSIONS = {'csv', 'json'}

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@share_bp.route('/share', methods=['GET', 'POST'])
def share():
    """
    Handle sharing Spotify data files.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in

    if request.method == 'POST':
        # Check if a file is uploaded
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            # Save the file
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)

            # Add file details to the database
            new_shared_data = SharedData(
                user_id=session['user_id'],
                file_path=file_path,
                file_name=filename,
                file_type=filename.rsplit('.', 1)[1].lower()
            )
            db.session.add(new_shared_data)
            db.session.commit()
            flash('File uploaded successfully!')
            return redirect(url_for('share.share'))

    # Retrieve all shared data for the logged-in user
    shared_data = SharedData.query.filter_by(user_id=session['user_id']).all()
    return render_template('share.html', shared_data=shared_data)

@share_bp.route('/share/delete/<int:data_id>', methods=['POST'])
def delete_shared_data(data_id):
    """
    Handle deleting shared data.
    """
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))  # Redirect to login if not logged in

    shared_data = SharedData.query.get_or_404(data_id)
    if shared_data.user_id != session['user_id']:
        return "Unauthorized", 403  # Prevent deleting data not owned by the user

    # Delete the file from the filesystem
    if os.path.exists(shared_data.file_path):
        os.remove(shared_data.file_path)

    # Delete the record from the database
    db.session.delete(shared_data)
    db.session.commit()
    flash('File deleted successfully!')
    return redirect(url_for('share.share'))
# Mock data for demonstration
mock_playlists = [
    {"id": 1, "name": "Chill Vibes", "song_count": 20},
    {"id": 2, "name": "Workout Hits", "song_count": 15},
    {"id": 3, "name": "Indie Mix", "song_count": 25},
]

mock_friends = [
    {"username": "alice"},
    {"username": "bob"},
    {"username": "charlie"},
]

