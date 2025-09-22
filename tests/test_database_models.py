from datetime import datetime

from app.models import Artist, Playlist, Track, User


def test_user_and_playlist_relationship(db_session_factory):
    with db_session_factory() as session:
        user = User(
            id="user-123",
            display_name="Test User",
            email="user@example.com",
            country="US",
        )
        playlist = Playlist(
            id="playlist-123",
            name="Integration Playlist",
            owner=user,
        )
        session.add_all([user, playlist])

    with db_session_factory() as session:
        stored_user = session.query(User).filter_by(id="user-123").one()
        assert stored_user.playlists[0].name == "Integration Playlist"
        assert stored_user.playlists[0].owner_id == "user-123"


def test_track_artist_association(db_session_factory):
    with db_session_factory() as session:
        artist = Artist(id="artist-1", name="Artist One")
        track = Track(id="track-1", name="Track One")
        track.artists.append(artist)
        session.add_all([artist, track])

    with db_session_factory() as session:
        stored_track = session.query(Track).filter_by(id="track-1").one()
        assert stored_track.artists[0].id == "artist-1"
        assert stored_track.artists[0].name == "Artist One"


def test_timestamp_fields_are_populated(db_session_factory):
    with db_session_factory() as session:
        user = User(id="user-time", display_name="Timer")
        session.add(user)

    with db_session_factory() as session:
        stored_user = session.query(User).filter_by(id="user-time").one()
        assert isinstance(stored_user.created_at, datetime)
        assert isinstance(stored_user.updated_at, datetime)
