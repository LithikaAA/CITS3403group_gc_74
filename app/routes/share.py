from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from flask_login import login_required, current_user
from ..models import db, User, Playlist, Share, SharedData
import os

share_bp = Blueprint('share', __name__, url_prefix='/share')

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

# ---------- Share a Playlist with a Friend ----------
@share_bp.route('/', methods=['GET', 'POST'])
@login_required
def share():
    playlists = Playlist.query.filter_by(owner_id=current_user.id).all()
    friends = User.query.filter(User.id != current_user.id).all()

    if request.method == 'POST':
        selected_ids = request.form.getlist('selected_playlists')
        friend_username = request.form.get('friend_username')

        if not selected_ids:
            flash('Please select at least one playlist to share.', 'error')
            return redirect(url_for('share.share'))

        friend = User.query.filter_by(username=friend_username).first()
        if not friend:
            flash('Friend not found.', 'error')
            return redirect(url_for('share.share'))

        for pid in selected_ids:
            new_share = Share(
                playlist_id=int(pid),
                recipient_id=friend.id,
                owner_id=current_user.id
            )
            db.session.add(new_share)
        db.session.commit()

        flash(f'Shared {len(selected_ids)} playlist(s) with {friend.username}!', 'success')
        return redirect(url_for('share.share'))

    return render_template('share.html', playlists=playlists, friends=friends)

# ---------- Handle Uploads of Shared Spotify Data ----------
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
                user_id=current_user.id,
                file_path=file_path,
                file_name=filename,
                file_type=filename.rsplit('.', 1)[1].lower()
            )
            db.session.add(new_shared_data)
            db.session.commit()
            flash('File uploaded successfully!')
            return redirect(url_for('share.upload_shared_data'))

    shared_data = SharedData.query.filter_by(user_id=current_user.id).all()
    return render_template('share_upload.html', shared_data=shared_data)

# ---------- Delete Uploaded Shared Data ----------
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

# ---------- View Shared Playlists Shared With You ----------
@share_bp.route('/shared')
@login_required
def shared_dashboard():
    # 1. Fetch all shares for this user
    shares = Share.query.filter_by(recipient_id=current_user.id).all()

    # 2. Flash if nothing’s been shared, but don’t redirect
    if not shares:
        flash('No playlists have been shared with you yet.', 'info')
        owner = None
    else:
        # 3. Use the owner of the first shared item for the header
        owner = shares[0].owner

    # 4. Build the list of shared_items
    shared_items = []
    for share in shares:
        playlist = share.playlist
        if playlist:
            track_data = playlist.track_data_as_chart()
            shared_items.append({
                'playlist_id': playlist.id,
                'title':       playlist.name,
                'labels':      track_data.get('labels', []),
                'values':      track_data.get('counts', [])
            })

    # 5. Always render the template
    return render_template(
        'shared_dashboard.html',
        shared_items=shared_items,
        owner=owner
    )
