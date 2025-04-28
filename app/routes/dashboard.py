from flask import Blueprint, render_template, session, redirect, url_for

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def dashboard():
    """
    Render the user dashboard.
    """
    if 'user_id' not in session:
        # Redirect to login if the user is not logged in
        return redirect(url_for('auth.login'))

    # Debugging: Print session data
    print("Session data:", session)

    return render_template('dashboard.html', username=session.get('username'))
    # Mock Data for Summary Cards
    summary = {
        "total_songs": 1245,
        "total_hours": 312,
        "unique_artists": 98,
        "top_genre": "Pop"
    }

    # Mock Data for Bar Chart (Songs Played by Month)
    songs_by_month = {
        "labels": ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct'],
        "data": [45, 60, 50, 70, 90, 65, 80, 75, 60, 85]
    }

    # Mock Data for Pie Chart (Genre Distribution)
    genre_distribution = {
        "labels": ['Pop', 'Rock', 'Hip-Hop', 'Jazz', 'Other'],
        "data": [40, 25, 20, 10, 5]
    }

    # Top 5 Artists List
    top_artists = ["The Weeknd", "Dua Lipa", "Ed Sheeran", "Taylor Swift", "Drake"]

    # Top 5 Songs List
    top_songs = ["Blinding Lights", "Levitating", "Shape of You", "Anti-Hero", "God's Plan"]

    return render_template(
        'dashboard.html',
        summary=summary,
        songs_by_month=songs_by_month,
        genre_distribution=genre_distribution,
        top_artists=top_artists,
        top_songs=top_songs
    )
