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
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

@share_bp.route('/shared')
@login_required
def shared_dashboard():
    shares = Share.query.filter_by(recipient_id=current_user.id).all()

    shared_items = []
    for share in shares:
        playlist = share.playlist
        if playlist:
            track_data = playlist.track_data_as_chart()
            shared_items.append({
                'owner': share.owner,
                'title': playlist.name,
                'labels': track_data.get('labels', []),
                'data': track_data.get('counts', [])
            })

    # Hardcoded comparison mock data
    comparison_minutes = {
        'labels': ['Song A', 'Song B', 'Song C'],
        'your_data': [120, 95, 80],
        'friend_data': [100, 110, 60]
    }

    comparison_bubble = {
        'you': [{'x': 0.6, 'y': 0.7, 'r': 10}, {'x': 0.4, 'y': 0.5, 'r': 8}],
        'friend': [{'x': 0.7, 'y': 0.6, 'r': 9}, {'x': 0.5, 'y': 0.4, 'r': 7}]
    }

    comparison_mood = {
        'you': [0.7, 0.6, 0.8, 0.3, 0.5],
        'friend': [0.5, 0.7, 0.6, 0.4, 0.6]
    }

    comparison_mode = {
        'you': [300, 120],
        'friend': [250, 180]
    }

    shared_summary = {
        'common_track': 'Song A',
        'your_avg_tempo': 120,
        'friend_avg_tempo': 115,
        'your_total_minutes': 450,
        'friend_total_minutes': 430,
        'your_mood': 'Energetic',
        'friend_mood': 'Chill'
    }

    top_artists_user = ['Artist 1', 'Artist 2', 'Artist 3', 'Artist 4', 'Artist 5']
    top_artists_friend = ['Artist A', 'Artist B', 'Artist C', 'Artist D', 'Artist E']

    return render_template(
        'shared_dashboard.html',
        shared_items=shared_items,
        comparison_minutes=comparison_minutes,
        comparison_bubble=comparison_bubble,
        comparison_mood=comparison_mood,
        comparison_mode=comparison_mode,
        shared_summary=shared_summary,
        top_artists_user=top_artists_user,
        top_artists_friend=top_artists_friend,
        friends_list=[]
    )
