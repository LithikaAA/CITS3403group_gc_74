from flask import Blueprint, render_template, request, redirect, url_for, flash

share_bp = Blueprint('share', __name__)

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

@share_bp.route('/share', methods=['GET', 'POST'])
def share():
    if request.method == 'POST':
        selected_playlists = request.form.getlist('selected_playlists')
        friend_username = request.form.get('friend_username')

        if not selected_playlists:
            flash('Please select at least one playlist to share.', 'error')
            return redirect(url_for('share.share'))

        # Mock sharing logic
        flash(f'Shared {len(selected_playlists)} playlist(s) with {friend_username}!', 'success')
        return redirect(url_for('share.share'))

    # On GET, render the form
    return render_template('share.html', playlists=mock_playlists, friends=mock_friends)
