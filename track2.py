import pandas as pd
from app.models import db, Track
from datetime import datetime, timezone
from app import create_app

app = create_app()
with app.app_context():
    df = pd.read_csv("spotifydataset.csv")

    # Drop duplicates before processing
    df.drop_duplicates(subset=["track_name", "artists"], inplace=True)

    new_tracks = []
    for _, row in df.iterrows():
        if pd.isna(row['track_name']) or pd.isna(row['artists']) or pd.isna(row['track_genre']):
            continue

        # Split artists if multiple (assuming ';' is the delimiter)
        artist_list = [a.strip() for a in str(row['artists']).split(';') if a.strip()]
        
        for artist in artist_list:
            # Check for existing track with same title and individual artist
            exists = db.session.query(Track).filter_by(
                title=row['track_name'],
                artist=artist
            ).first()
            if exists:
                continue

            new_track = Track(
                title=row['track_name'],
                artist=artist,
                genre=row['track_genre'],
                tempo=row.get('tempo', 0) or 0,
                valence=row.get('valence', 0) or 0,
                energy=row.get('energy', 0) or 0,
                acousticness=row.get('acousticness', 0) or 0,
                liveness=row.get('liveness', 0) or 0,
                danceability=row.get('danceability', 0) or 0,
                mode=int(row.get('mode', 1)) if not pd.isna(row.get('mode')) else 1,
                date_played=datetime.now(timezone.utc)
            )
            new_tracks.append(new_track)

    db.session.bulk_save_objects(new_tracks)
    db.session.commit()
    print(f"Inserted {len(new_tracks)} unique tracks (with individual artists).")
