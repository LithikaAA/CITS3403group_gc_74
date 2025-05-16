import os
import pandas as pd
import difflib
import unicodedata
import re
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables
load_dotenv()

# Set up Spotipy client
auth_manager = SpotifyClientCredentials(
    client_id=os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIPY_CLIENT_SECRET")
)
sp = spotipy.Spotify(auth_manager=auth_manager)

# Load local CSV metadata
df = pd.read_csv("data/spotify.csv")
df.columns = df.columns.str.strip()
df["track_id"] = df["track_id"].astype(str)

# Unicode-safe normalization for multilingual support
def normalize_str(s):
    if pd.isna(s):
        return ""
    return unicodedata.normalize('NFKC', str(s)).casefold().strip()

# Preprocess the DataFrame for faster lookups
def preprocess_dataframe():
    global df
    # Create normalized columns for fuzzy matching
    df['normalized_track_name'] = df['track_name'].apply(normalize_str)
    df['normalized_artists'] = df['artists'].apply(normalize_str)

    # Extract numerical features for track similarity
    numerical_features = ['danceability', 'energy', 'valence', 'tempo', 'acousticness', 'liveness']
    for col in numerical_features:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    print(f"Preprocessed dataframe with {len(df)} rows")
    return df

# Get metadata from CSV directly by track title and artist
def get_metadata_by_title_artist(title, artist):
    normalized_title = normalize_str(title)
    normalized_artist = normalize_str(artist)

    exact_matches = df[
        (df['normalized_track_name'] == normalized_title)
    ]

    if not exact_matches.empty:
        def artist_match_score(csv_artists):
            artist_list = re.split(r'[;&,]', normalize_str(csv_artists))
            return max([
                difflib.SequenceMatcher(None, normalized_artist, a.strip()).ratio()
                for a in artist_list
            ] + [0])

        exact_matches['artist_score'] = exact_matches['normalized_artists'].apply(artist_match_score)
        best_match = exact_matches.sort_values('artist_score', ascending=False).iloc[0]

        if best_match['artist_score'] > 0.7:
            print(f"Found exact title match with artist score {best_match['artist_score']}")
            return best_match

    possible_titles = difflib.get_close_matches(
        normalized_title,
        df['normalized_track_name'].unique(),
        n=10,
        cutoff=0.7
    )

    if possible_titles:
        candidates = df[df['normalized_track_name'].isin(possible_titles)]

        def combined_score(row):
            title_score = difflib.SequenceMatcher(None, normalized_title, row['normalized_track_name']).ratio()
            artist_list = re.split(r'[;&,]', row['normalized_artists'])
            artist_score = max([
                difflib.SequenceMatcher(None, normalized_artist, a.strip()).ratio()
                for a in artist_list
            ] + [0])
            return (title_score * 0.6) + (artist_score * 0.4)

        candidates['match_score'] = candidates.apply(combined_score, axis=1)
        best_match = candidates.sort_values('match_score', ascending=False).iloc[0]
        if best_match['match_score'] > 0.7:
            print(f"Found fuzzy match with score {best_match['match_score']}: {best_match['track_name']} by {best_match['artists']}")
            return best_match

    artist_matches = df[df['normalized_artists'].str.contains(normalized_artist, regex=False)]
    if not artist_matches.empty:
        if 'popularity' in artist_matches.columns:
            best_match = artist_matches.sort_values('popularity', ascending=False).iloc[0]
        else:
            best_match = artist_matches.iloc[0]
        print(f"Found fallback match by artist: {best_match['track_name']}")
        return best_match

    print("No suitable match found in local data")
    return None

# Enhanced enrichment function with multiple fallback strategies
def enrich_metadata(track_id, fallback_title=None, fallback_artist=None):
    print(f"Trying enrichment for track ID: {track_id}")

    row = df[df["track_id"] == track_id]

    if not row.empty:
        print(f"Found direct track_id match: {row.iloc[0]['track_name']}")
        return extract_metadata(row.iloc[0])

    if track_id and len(track_id) > 8:
        try:
            track_features = sp.audio_features(track_id)
            if track_features and track_features[0]:
                print(f"Retrieved features directly from Spotify API")
                duration_ms = track_features[0].get("duration_ms", 0)
                duration_min = round(duration_ms / 60000, 2)

                api_data = {
                    "danceability": round(track_features[0].get("danceability", 0), 3),
                    "energy": round(track_features[0].get("energy", 0), 3),
                    "liveness": round(track_features[0].get("liveness", 0), 3),
                    "acousticness": round(track_features[0].get("acousticness", 0), 3),
                    "valence": round(track_features[0].get("valence", 0), 3),
                    "tempo": round(track_features[0].get("tempo", 0), 2),
                    "mode": "Major" if track_features[0].get("mode", 0) == 1 else "Minor",
                    "duration_ms": duration_ms,
                    "duration_min": duration_min
                }

                track_info = sp.track(track_id)
                if track_info and track_info.get('artists') and len(track_info['artists']) > 0:
                    artist_id = track_info['artists'][0]['id']
                    artist_info = sp.artist(artist_id)
                    if artist_info and 'genres' in artist_info and len(artist_info['genres']) > 0:
                        api_data["genre"] = artist_info['genres'][0]

                return api_data
        except Exception as e:
            print(f"Error retrieving from Spotify API: {e}")

    if fallback_title and fallback_artist:
        csv_match = get_metadata_by_title_artist(fallback_title, fallback_artist)
        if csv_match is not None:
            return extract_metadata(csv_match)

    print("No match found via any method")
    return generate_default_metadata()

# Extract consistent metadata from a dataframe row
def extract_metadata(row):
    duration_ms = int(row.get("duration_ms", 0))
    duration_min = round(duration_ms / 60000, 2)

    return {
        "genre": str(row.get("track_genre", "")).strip() or "Unknown",
        "duration_ms": duration_ms,
        "duration_min": duration_min,
        "danceability": round(float(row.get("danceability", 0)), 3),
        "energy": round(float(row.get("energy", 0)), 3),
        "liveness": round(float(row.get("liveness", 0)), 3),
        "acousticness": round(float(row.get("acousticness", 0)), 3),
        "valence": round(float(row.get("valence", 0)), 3),
        "tempo": round(float(row.get("tempo", 0)), 2),
        "mode": "Major" if int(row.get("mode", 0)) == 1 else "Minor"
    }

# Generate minimal default metadata when all else fails
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

# Combines Spotify API base metadata with local enrichment
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

        enriched = enrich_metadata(track_id, fallback_title=name, fallback_artist=artist)
        print(f"Enriched result for '{name}' by '{artist}':", enriched)

        base = {
            'id': track_id,
            'name': name,
            'artist': artist,
            'album': album,
            'image': image_url
        }
        full_track = {**base, **enriched}

        if 'duration_ms' in full_track:
            ms = full_track['duration_ms']
            minutes = int(ms / 60000)
            seconds = int((ms % 60000) / 1000)
            full_track['duration'] = f"{minutes}:{seconds:02d}"

        tracks.append(full_track)

    return tracks

# Initialize data preprocessing when module loads
preprocess_dataframe()