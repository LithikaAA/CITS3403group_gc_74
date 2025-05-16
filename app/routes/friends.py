from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from sqlalchemy import func
import sqlalchemy as sa

from app.models     import db, User, Friend, Track, UserTrack
from app.forms      import AddFriendForm, AcceptFriendForm

friends_bp = Blueprint('friends', __name__)

@friends_bp.route('/add-friend', methods=['GET', 'POST'])
@login_required
def add_friend():
    form = AddFriendForm()
    if form.validate_on_submit():
        username = form.friend_username.data.strip()
        # 1) Does that user exist?
        friend = User.query.filter_by(username=username).first()
        if not friend:
            flash(f'No user found with username “{username}”.', 'error')
            return redirect(url_for('friends.add_friend'))
        # 2) No self-adds
        if friend.id == current_user.id:
            flash("You can’t add yourself as a friend.", 'error')
            return redirect(url_for('friends.add_friend'))
        # 3) No duplicate requests
        existing = Friend.query.filter_by(
            user_id=current_user.id,
            friend_id=friend.id
        ).first()
        if existing:
            if existing.is_accepted:
                flash(f'You’re already friends with {friend.username}.', 'info')
            else:
                flash(f'Friend request already pending to {friend.username}.', 'info')
        else:
            # create a 1-way request; they’ll accept to make it mutual
            db.session.add(Friend(
                user_id=current_user.id,
                friend_id=friend.id,
                is_accepted=False
            ))
            db.session.commit()
            flash(f'Friend request sent to {friend.username}!', 'success')
        return redirect(url_for('friends.add_friend'))

    # ----- on GET: build “top_friends” list ----- #
    # your avg BPM
    my_bpm = db.session.query(func.avg(Track.tempo)) \
        .join(UserTrack, UserTrack.track_id == Track.id) \
        .filter(UserTrack.user_id == current_user.id) \
        .scalar() or 0

    # helper to project id, username, pic, avg_bpm
    def base_friend_q(filter_clause):
        return (
            db.session.query(
                User.id.label("id"),
                User.username.label("username"),
                User.profile_pic.label("profile_pic"),
                func.avg(Track.tempo).label("avg_bpm")
            )
            .join(Friend, filter_clause)
            .join(UserTrack, UserTrack.user_id == User.id)
            .join(Track, Track.id == UserTrack.track_id)
            .filter(Friend.is_accepted == True)
            .group_by(User.id)
        )

    # outgoing = me ➞ them
    outgoing = base_friend_q(Friend.friend_id == User.id) \
        .filter(Friend.user_id == current_user.id)
    # incoming = them ➞ me
    incoming = base_friend_q(Friend.user_id == User.id) \
        .filter(Friend.friend_id == current_user.id)

    # union them, then compute |avg_bpm – my_bpm|, sort & limit
    union_sq = outgoing.union_all(incoming).subquery()
    friends_with_diff = (
        db.session.query(
            union_sq.c.id,
            union_sq.c.username,
            union_sq.c.profile_pic,
            sa.func.abs(union_sq.c.avg_bpm - my_bpm).label("bpm_diff")
        )
        .order_by("bpm_diff")
        .limit(20)
        .all()
    )

    seen = set()
    unique = []
    for row in friends_with_diff:
        if row.id not in seen:
            seen.add(row.id)
            unique.append(row)

    friends_with_diff = unique

    top_friends = []
    for row in friends_with_diff:
        u = User(id=row.id, username=row.username, profile_pic=row.profile_pic)
        # attach the difference so you can show it if you like
        u.bpm_diff = row.bpm_diff
        top_friends.append(u)

    # outstanding friend-requests
    incoming_requests = current_user.incoming_friend_requests()
    sent_requests     = current_user.sent_friend_requests()
    accept_form       = AcceptFriendForm()

    return render_template(
        'add_friends.html',
        form=form,
        top_friends=top_friends,
        incoming_requests=incoming_requests,
        sent_requests=sent_requests,
        accept_form=accept_form
    )
    
@friends_bp.route('/friends/remove/<username>', methods=['POST'])
@login_required
def remove_friend(username):
    friend = User.query.filter_by(username=username).first()
    if not friend:
        return jsonify({'status': 'error', 'message': 'User not found'}), 404

    # Remove both directions if needed
    deleted = False

    friendship = Friend.query.filter_by(user_id=current_user.id, friend_id=friend.id).first()
    if friendship:
        db.session.delete(friendship)
        deleted = True

    reverse = Friend.query.filter_by(user_id=friend.id, friend_id=current_user.id).first()
    if reverse:
        db.session.delete(reverse)
        deleted = True

    if deleted:
        db.session.commit()
        return jsonify({'status': 'success', 'message': f'Removed {username} from friends'})
    else:
        return jsonify({'status': 'error', 'message': 'Friendship not found'}), 400

@friends_bp.route('/friends/list')
@login_required
def list_friends():
    # Updated to use the property instead of the method
    friends = current_user.all_friends
    return jsonify({"friends": [{"username": f.username} for f in friends]})

@friends_bp.route('/friends/accept/<int:request_id>', methods=['POST'])
@login_required
def accept_friend(request_id):
    request = Friend.query.get_or_404(request_id)

    if request.friend_id != current_user.id:
        return "Unauthorized", 403

    request.is_accepted = True

    # Add reverse friendship
    db.session.add(Friend(
        user_id=current_user.id,
        friend_id=request.user_id,
        is_accepted=True
    ))
    db.session.commit()

    flash("Friend request accepted!", "success")
    return redirect(url_for('friends.add_friend'))

@friends_bp.route('/friends/decline/<int:request_id>', methods=['POST'])
@login_required
def decline_friend(request_id):
    request = Friend.query.get_or_404(request_id)

    if request.friend_id != current_user.id:
        return "Unauthorized", 403

    db.session.delete(request)
    db.session.commit()

    flash("Friend request declined.", "info")
    return redirect(url_for('friends.add_friend'))
