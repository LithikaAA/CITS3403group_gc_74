import os
import pandas as pd
import difflib
import unicodedata
import re
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

# Load environment variables
load_dotenv()

# ---------- OAuth for user-level login ----------
def get_spotify_auth_manager(username=None):
    return SpotifyOAuth(
        client_id=os.getenv("SPOTIPY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIPY_CLIENT_SECRET"),
        redirect_uri=os.getenv("SPOTIPY_REDIRECT_URI"),
        scope="user-read-recently-played",
        cache_path=f".cache-{username}" if username else ".cache"
    )

# ---------- Spotipy client for app-level access ----------
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# ---------- Load CSV metadata ----------
df = pd.read_csv("spotify.csv")
df.columns = df.columns.str.strip()
df["track_id"] = df["track_id"].astype(str)

# ---------- Unicode-safe normalization for fuzzy matching ----------
def normalize_str(s):
    if pd.isna(s):
        return ""
    return unicodedata.normalize('NFKC', str(s)).casefold().strip()

# Preprocess DataFrame for faster fuzzy matching
def preprocess_dataframe():
    global df
    df['normalized_track_name'] = df['track_name'].apply(normalize_str)
    df['normalized_artists'] = df['artists'].apply(normalize_str)
    for col in ['danceability', 'energy', 'valence', 'tempo', 'acousticness', 'liveness']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

preprocess_dataframe()

# ---------- Fuzzy matching by track title + artist ----------
def get_metadata_by_title_artist(title, artist):
    normalized_title = normalize_str(title)
    normalized_artist = normalize_str(artist)

    exact_matches = df[df['normalized_track_name'] == normalized_title]

    if not exact_matches.empty:
        def artist_score(row):
            candidates = re.split(r'[;&,]', normalize_str(row))
            return max([difflib.SequenceMatcher(None, normalized_artist, a).ratio() for a in candidates] + [0])

        exact_matches['artist_score'] = exact_matches['normalized_artists'].apply(artist_score)
        best = exact_matches.sort_values('artist_score', ascending=False).iloc[0]
        if best['artist_score'] > 0.7:
            return best

    possible_titles = difflib.get_close_matches(normalized_title, df['normalized_track_name'], n=10, cutoff=0.7)
    if possible_titles:
        candidates = df[df['normalized_track_name'].isin(possible_titles)]

        def combined_score(row):
            title_sim = difflib.SequenceMatcher(None, normalized_title, row['normalized_track_name']).ratio()
            artist_sim = max([difflib.SequenceMatcher(None, normalized_artist, a.strip()).ratio()
                              for a in re.split(r'[;&,]', row['normalized_artists'])] + [0])
            return title_sim * 0.6 + artist_sim * 0.4

        candidates['match_score'] = candidates.apply(combined_score, axis=1)
        best = candidates.sort_values('match_score', ascending=False).iloc[0]
        if best['match_score'] > 0.7:
            return best

    artist_only = df[df['normalized_artists'].str.contains(normalized_artist, regex=False)]
    if not artist_only.empty:
        return artist_only.sort_values('popularity', ascending=False).iloc[0] if 'popularity' in artist_only.columns else artist_only.iloc[0]

    return None

# ---------- Metadata extraction from row ----------
def extract_metadata(row):
    duration_ms = int(row.get("duration_ms", 0))
    return {
        "genre": str(row.get("track_genre", "")).strip() or "Unknown",
        "duration_ms": duration_ms,
        "duration_min": round(duration_ms / 60000, 2),
        "danceability": round(float(row.get("danceability", 0)), 3),
        "energy": round(float(row.get("energy", 0)), 3),
        "liveness": round(float(row.get("liveness", 0)), 3),
        "acousticness": round(float(row.get("acousticness", 0)), 3),
        "valence": round(float(row.get("valence", 0)), 3),
        "tempo": round(float(row.get("tempo", 0)), 2),
        "mode": "Major" if int(row.get("mode", 0)) == 1 else "Minor"
    }

# ---------- Fallback default metadata ----------
def generate_default_metadata():
    return {
        "genre": "Unknown",
        "duration_ms": 0,
        "duration_min": 0.0,
        "danceability": 0.5,
        "energy": 0.5,
        "liveness": 0.5,
        "acousticness": 0.5,
        "valence": 0.5,
        "tempo": 120.0,
        "mode": "Major"
    }

# ---------- Main enrichment logic ----------
def enrich_metadata(track_id, fallback_title=None, fallback_artist=None):
    row = df[df["track_id"] == track_id]
    if not row.empty:
        return extract_metadata(row.iloc[0])

    try:
        features = sp.audio_features(track_id)
        if features and features[0]:
            base = features[0]
            duration_ms = base.get("duration_ms", 0)
            metadata = {
                "duration_ms": duration_ms,
                "duration_min": round(duration_ms / 60000, 2),
                "danceability": round(base.get("danceability", 0), 3),
                "energy": round(base.get("energy", 0), 3),
                "liveness": round(base.get("liveness", 0), 3),
                "acousticness": round(base.get("acousticness", 0), 3),
                "valence": round(base.get("valence", 0), 3),
                "tempo": round(base.get("tempo", 0), 2),
                "mode": "Major" if base.get("mode", 0) == 1 else "Minor",
                "genre": "Unknown"
            }

            track_info = sp.track(track_id)
            if track_info and track_info['artists']:
                artist_id = track_info['artists'][0]['id']
                genres = sp.artist(artist_id).get("genres", [])
                if genres:
                    metadata["genre"] = genres[0]

            return metadata
    except Exception as e:
        print(f"[enrich_metadata] Spotify API failed: {e}")

    if fallback_title and fallback_artist:
        fallback_row = get_metadata_by_title_artist(fallback_title, fallback_artist)
        if fallback_row is not None:
            return extract_metadata(fallback_row)

    return generate_default_metadata()

# ---------- Search + merge ----------
def search_tracks(query, limit=10):
    results = sp.search(q=query, limit=limit, type='track')
    tracks = []

    for item in results.get('tracks', {}).get('items', []):
        track_id = item.get('id', '')
        name = item.get('name', '')
        artist = item['artists'][0]['name'] if item.get('artists') else 'Unknown Artist'
        album = item['album']['name'] if item.get('album') else 'Unknown Album'
        images = item['album'].get('images') if item.get('album') else []
        image_url = images[0]['url'] if images else ''

        base = {
            'id': track_id,
            'name': name,
            'artist': artist,
            'album': album,
            'image': image_url
        }

        enriched = enrich_metadata(track_id, fallback_title=name, fallback_artist=artist)
        full_track = {**base, **enriched}

        if 'duration_ms' in full_track:
            ms = full_track['duration_ms']
            full_track['duration'] = f"{int(ms / 60000)}:{int((ms % 60000) / 1000):02d}"

        tracks.append(full_track)

    return tracks
