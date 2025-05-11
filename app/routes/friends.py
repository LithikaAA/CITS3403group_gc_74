from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from app.models import User, Track, UserTrack, Friend
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from ..models import db, User, Friend, Track
from ..forms import AddFriendForm
import sqlalchemy as sa

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/add-friend', methods=['GET', 'POST'])
@login_required
def add_friend():
    form = AddFriendForm()
    if form.validate_on_submit():
        username = form.friend_username.data.strip()
        friend = User.query.filter_by(username=username).first()

        if not friend:
            flash(f'No user found with username "{username}"', 'error')
        elif friend.id == current_user.id:
            flash("You can't add yourself as a friend.", 'error')
        else:
            existing = Friend.query.filter_by(
                user_id=current_user.id,
                friend_id=friend.id
            ).first()
            if existing:
                flash(f'{friend.username} is already your friend.', 'info')
            else:
                db.session.add(Friend(user_id=current_user.id, friend_id=friend.id))
                db.session.commit()
                flash(f'{friend.username} added successfully!', 'success')
        return redirect(url_for('friends.add_friend'))  

    # Compute current user's average BPM using UserTrack
    my_bpm = db.session.query(sa.func.avg(Track.tempo)) \
        .join(UserTrack, UserTrack.track_id == Track.id) \
        .filter(UserTrack.user_id == current_user.id) \
        .scalar() or 0

    # Fetch friends and order by BPM similarity
    top_friends = (
        db.session.query(User)
        .join(Friend, Friend.friend_id == User.id)
        .join(UserTrack, UserTrack.user_id == User.id)
        .join(Track, Track.id == UserTrack.track_id)
        .filter(Friend.user_id == current_user.id, Friend.is_accepted == True)
        .group_by(User.id)
        .order_by(sa.func.abs(sa.func.avg(Track.tempo) - my_bpm))
        .limit(20)
        .all()
    )

    incoming_requests = current_user.incoming_friend_requests()
    sent_requests = current_user.sent_friend_requests()
    new_friend_usernames = [r.user.username for r in incoming_requests]

    return render_template (
        'add_friends.html',
        form=form,
        top_friends=top_friends,
        incoming_requests=incoming_requests,
        sent_requests=sent_requests,
        new_friend_usernames=new_friend_usernames,
    )

    
@friends_bp.route('/friends/remove/<username>', methods=['POST'])
@login_required
def remove_friend(username):
    friend = User.query.filter_by(username=username).first()
    if not friend:
        return jsonify({'error': 'User not found'}), 404

    # Remove friendship from both directions
    Friend.query.filter_by(user_id=current_user.id, friend_id=friend.id).delete()
    Friend.query.filter_by(user_id=friend.id, friend_id=current_user.id).delete()
    db.session.commit()
    return jsonify({'message': 'Friend removed'}), 200

@friends_bp.route('/friends/list')
@login_required
def list_friends():
    # Updated to use the property instead of the method
    friends = current_user.all_friends
    return jsonify({"friends": [{"username": f.username} for f in friends]})