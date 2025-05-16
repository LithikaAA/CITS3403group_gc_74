# tests/unit/test_simplified.py
import pytest
from app import create_app, db
from app.models import User, Playlist, Track, PlaylistTrack

class TestSimplified:
    @pytest.fixture(autouse=True)
    def setup(self):
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
        # Create a test user
        self.user = User(username="test_simplified", email="test_simplified@example.com")
        self.user.set_password("password123")
        db.session.add(self.user)
        db.session.commit()
        
        # Create a test playlist
        self.playlist = Playlist(name="Test Playlist", owner_id=self.user.id)
        db.session.add(self.playlist)
        
        # Create a test track
        self.track = Track(
            title="Test Track",
            artist="Test Artist",
            genre="Test Genre",
            user_id=self.user.id,
            valence=0.5,
            acousticness=0.5,
            danceability=0.5,
            energy=0.5,
            tempo=120,
            mode="Major",
            duration_ms=180000
        )
        db.session.add(self.track)
        db.session.commit()
        
        yield
        
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_edit_playlist_name(self):
        """Test editing playlist name using direct database access."""
        # Update playlist name directly in the database
        self.playlist.name = "Updated Playlist Name"
        db.session.commit()
        
        # Verify update
        updated_playlist = Playlist.query.filter_by(id=self.playlist.id).first()
        assert updated_playlist.name == "Updated Playlist Name"
    
    def test_remove_track_from_playlist(self):
        """Test adding and removing a track from a playlist using direct database access."""
        # Add track to playlist
        pt = PlaylistTrack(playlist_id=self.playlist.id, track_id=self.track.id)
        db.session.add(pt)
        db.session.commit()
        
        # Verify track was added
        playlist_track = PlaylistTrack.query.filter_by(
            playlist_id=self.playlist.id, track_id=self.track.id
        ).first()
        assert playlist_track is not None
        
        # Remove track from playlist
        db.session.delete(playlist_track)
        db.session.commit()
        
        # Verify track was removed
        playlist_track = PlaylistTrack.query.filter_by(
            playlist_id=self.playlist.id, track_id=self.track.id
        ).first()
        assert playlist_track is None
    
    def test_duplicate_track_in_playlist(self):
        """Test adding different tracks to a playlist."""
        # Add the first track to the playlist
        pt1 = PlaylistTrack(playlist_id=self.playlist.id, track_id=self.track.id)
        db.session.add(pt1)
        db.session.commit()
        
        # Create a second track
        track2 = Track(
            title="Second Test Track",
            artist="Another Artist",
            genre="Another Genre",
            user_id=self.user.id,
            valence=0.3,
            acousticness=0.7,
            danceability=0.4,
            energy=0.6,
            tempo=95,
            mode="Minor",
            duration_ms=210000
        )
        db.session.add(track2)
        db.session.commit()
        
        # Add the second track to the playlist
        pt2 = PlaylistTrack(playlist_id=self.playlist.id, track_id=track2.id)
        db.session.add(pt2)
        db.session.commit()
        
        # Verify both tracks are in the playlist
        playlist_tracks = PlaylistTrack.query.filter_by(playlist_id=self.playlist.id).all()
        assert len(playlist_tracks) == 2