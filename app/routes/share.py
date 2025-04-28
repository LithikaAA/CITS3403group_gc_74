from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import db, User, Playlist, Share

share_bp = Blueprint('share', __name__, url_prefix='/share')

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

# ---------- View Shared With You ----------
@share_bp.route('/shared')
@login_required
def shared_dashboard():
    shares = Share.query.filter_by(recipient_id=current_user.id).all()

    shared_items = []
    for share in shares:
        playlist = share.playlist
        if playlist:
            track_data = playlist.track_data_as_chart()  # You'll need to define this helper
            shared_items.append({
                'owner': share.owner,
                'title': playlist.name,
                'labels': track_data.get('labels', []),
                'data': track_data.get('counts', [])
            })

    return render_template('shared_dashboard.html', shared_items=shared_items)