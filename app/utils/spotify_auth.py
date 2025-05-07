import os
import pandas as pd
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

# Load environment variables
load_dotenv()

# ---------- SpotifyOAuth: for user-level login ----------
def get_spotify_auth_manager(username=None):
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-read-recently-played",
        cache_path=f".cache-{username}" if username else ".cache"
    )

# ---------- Spotipy client: app-level access ----------
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# ---------- Load CSV metadata ----------
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

        base = {
            'id': track_id,
            'name': item.get('name', ''),
            'artist': artist,
            'album': album,
            'image': image_url
        }
        enriched = enrich_metadata(track_id)
        tracks.append({**base, **enriched})

    return tracks

def get_audio_features(track_ids):
    """Fetch audio features from Spotify API for a list of track IDs."""
    features = []
    for track_id in track_ids:
        try:
            result = sp.audio_features(track_id)
            if result and result[0]:
                features.append(result[0])
        except Exception as e:
            print(f"[ERROR] Failed to fetch audio features for {track_id}: {e}")
    return features
