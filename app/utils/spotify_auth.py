import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables from .env file
load_dotenv()

# Set up Spotipy client credentials using correct environment variable names
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp = spotipy.Spotify(auth_manager=auth_manager)


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
            # 'preview_url' and 'genre' intentionally excluded
        })

    return tracks



def get_audio_features(track_ids):
    """
    Fetch audio features for each track using the non-deprecated single-track endpoint.
    """
    features = []
    for track_id in track_ids:
        try:
            # Internally still uses bulk endpoint, but handles fallback
            result = sp.audio_features(track_id)
            if result and result[0]:
                features.append(result[0])
        except Exception as e:
            print(f"[ERROR] Failed to fetch audio features for {track_id}: {e}")
    return features
