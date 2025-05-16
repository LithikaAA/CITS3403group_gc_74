import pandas as pd

# Load the full CSV just once at import
df = pd.read_csv("data/spotify.csv")

# Ensure clean column names and types
df.columns = df.columns.str.strip()
df["track_id"] = df["track_id"].astype(str)

def get_track_features_by_id(track_id):
    """
    Return enriched track metadata from local CSV for a given Spotify track ID.
    """
    row = df[df["track_id"] == track_id]
    if row.empty:
        return None

    row_data = row.iloc[0]
    return {
        "id": row_data["track_id"],
        "name": row_data["track_name"],
        "artist": row_data["artists"],
        "album": row_data["album_name"],
        "genre": row_data["track_genre"],
        "duration_ms": int(row_data["duration_ms"]),
        "danceability": round(row_data["danceability"], 3),
        "energy": round(row_data["energy"], 3),
        "liveness": round(row_data["liveness"], 3),
        "acousticness": round(row_data["acousticness"], 3),
        "valence": round(row_data["valence"], 3),
        "tempo": round(row_data["tempo"], 2),
        "mode": "Major" if row_data["mode"] == 1 else "Minor"
    }
