import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

# Load environment variables
load_dotenv()

# ---------- OAuth for user authentication (if needed) ----------
def get_spotify_auth_manager():
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-read-recently-played"
    )

# ---------- Client credentials for app-level access ----------
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# ---------- Search helper ----------
def search_tracks(query, limit=10):
    results = sp.search(q=query, limit=limit, type='track')
    tracks = []

    for item in results.get('tracks', {}).get('items', []):
        artist = item['artists'][0]['name'] if item.get('artists') else 'Unknown Artist'
        album = item['album']['name'] if item.get('album') else 'Unknown Album'
        images = item['album'].get('images') if item.get('album') else []
        image_url = images[0]['url'] if images else ''

        tracks.append({
            'id': item.get('id', ''),
            'name': item.get('name', ''),
            'artist': artist,
            'album': album,
            'image': image_url
        })

    return tracks

# ---------- Audio features helper ----------
def get_audio_features(track_ids):
    features = []
    for track_id in track_ids:
        try:
            result = sp.audio_features(track_id)
            if result and result[0]:
                features.append(result[0])
        except Exception as e:
            print(f"[ERROR] Failed to fetch audio features for {track_id}: {e}")
    return features
