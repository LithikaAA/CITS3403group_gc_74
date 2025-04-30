import pandas as pd
from app import create_app, db
from app.models import Track, Artist

app = create_app()
app.app_context().push()  # Ensure Flask app context for db operations

df = pd.read_csv('app/data/spotify.csv')

for _, row in df.iterrows():
    # Process and split multiple artists (assuming comma-separated in CSV)
    artist_names = [name.strip() for name in str(row['artists']).split(',')]

    # Create Track object
    track = Track(
        track_id=row['track_id'],
        track_name=row['track_name'],
        album_name=row['album_name'],
        popularity=row['popularity'],
        duration_ms=row['duration_ms'],
        explicit=row['explicit'],
        danceability=row['danceability'],
        energy=row['energy'],
        key=row['key'],
        loudness=row['loudness'],
        mode=row['mode'],
        speechiness=row['speechiness'],
        acousticness=row['acousticness'],
        instrumentalness=row['instrumentalness'],
        liveness=row['liveness'],
        valence=row['valence'],
        tempo=row['tempo'],
        time_signature=row['time_signature'],
        genre=row['track_genre']
    )

    db.session.add(track)

    # Associate artists
    for name in artist_names:
        artist = Artist.query.filter_by(name=name).first()
        if not artist:
            artist = Artist(name=name)
            db.session.add(artist)
            db.session.flush()  # Assigns an id to the new artist
        track.artists.append(artist)

db.session.commit()
print("Database populated successfully with tracks and artist relationships!")
