from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy.sql import func
from ..models import db, User, Friend, Track
from ..forms import AddFriendForm

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

    # On GET (or invalid POST), compute top_friends and render form:
    my_bpm = db.session.query(func.avg(Track.tempo)) \
                      .filter(Track.user_id == current_user.id) \
                      .scalar() or 0

    top_friends = (
        db.session.query(User)
        .join(Friend, Friend.friend_id == User.id)
        .join(Track, Track.user_id == User.id)
        .filter(Friend.user_id == current_user.id)
        .group_by(User.id)
        .order_by(func.abs(func.avg(Track.tempo) - my_bpm))
        .limit(10)
        .all()
    )

    return render_template(
        'add_friends.html',
        form=form,
        top_friends=top_friends
    )
