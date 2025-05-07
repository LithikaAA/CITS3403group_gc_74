import os
import pandas as pd
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables from .env file
load_dotenv()

# Set up Spotipy client credentials
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Load local CSV metadata
df = pd.read_csv("spotify.csv")
df.columns = df.columns.str.strip()
df["track_id"] = df["track_id"].astype(str)


def enrich_metadata(track_id):
    """Get matching metadata from the CSV based on track_id."""
    row = df[df["track_id"] == track_id]
    if row.empty:
        return {}

    r = row.iloc[0]
    return {
        "genre": r["track_genre"],
        "duration_ms": r["duration_ms"],
        "danceability": round(r["danceability"], 3),
        "energy": round(r["energy"], 3),
        "liveness": round(r["liveness"], 3),
        "acousticness": round(r["acousticness"], 3),
        "valence": round(r["valence"], 3),
        "tempo": round(r["tempo"], 2),
        "mode": "Major" if r["mode"] == 1 else "Minor"
    }


def search_tracks(query, limit=10):
    results = sp.search(q=query, limit=limit, type='track')
    tracks = []

    for item in results.get('tracks', {}).get('items', []):
        track_id = item.get('id', '')
        artist = item['artists'][0]['name'] if item.get('artists') else 'Unknown Artist'
        album = item['album']['name'] if item.get('album') else 'Unknown Album'
        images = item['album'].get('images') if item.get('album') else []
        image_url = images[0]['url'] if images else ''

        # Merge base + enriched
        base = {
            'id': track_id,
            'name': item.get('name', ''),
            'artist': artist,
            'album': album,
            'image': image_url
        }
        enriched = enrich_metadata(track_id)
        full_track = {**base, **enriched}

        tracks.append(full_track)

    return tracks
