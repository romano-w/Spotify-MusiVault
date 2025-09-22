from contextlib import contextmanager
from importlib import reload
from typing import Any, Dict, List, Optional

import pytest


class FakeSpotify:
    """A lightweight Spotipy stand-in for deterministic testing."""

    def __init__(self, **payload: Any) -> None:
        self._payload = payload
        self.calls: List[str] = []

    def _get(self, key: str, default: Any = None) -> Any:
        return self._payload.get(key, default)

    def current_user(self) -> Dict[str, Any]:
        self.calls.append("current_user")
        return self._get("current_user", {})

    def current_user_playlists(self) -> Dict[str, Any]:
        self.calls.append("current_user_playlists")
        return self._get(
            "current_user_playlists",
            {"items": [], "next": None},
        )

    def playlist(self, playlist_id: str) -> Dict[str, Any]:
        self.calls.append("playlist")
        playlists = self._get("playlist", {})
        return playlists.get(playlist_id, {}) if isinstance(playlists, dict) else playlists

    def playlist_items(self, playlist_id: str) -> Dict[str, Any]:
        self.calls.append("playlist_items")
        items = self._get("playlist_items", {})
        return items.get(playlist_id, {"items": [], "next": None}) if isinstance(items, dict) else items

    def playlist_cover_image(self, playlist_id: str) -> Any:
        self.calls.append("playlist_cover_image")
        images = self._get("playlist_cover_image", {})
        return images.get(playlist_id) if isinstance(images, dict) else images

    def track(self, track_id: str) -> Dict[str, Any]:
        self.calls.append("track")
        tracks = self._get("track", {})
        return tracks.get(track_id, {}) if isinstance(tracks, dict) else tracks

    def tracks(self, track_ids: List[str]) -> Dict[str, Any]:
        self.calls.append("tracks")
        return self._get("tracks", {"tracks": []})

    def current_user_saved_tracks(self) -> Dict[str, Any]:
        self.calls.append("current_user_saved_tracks")
        return self._get("current_user_saved_tracks", {"items": [], "next": None})

    def audio_features(self, track_ids: List[str]) -> List[Dict[str, Any]]:
        self.calls.append("audio_features")
        features = self._get("audio_features", [])
        return features if isinstance(features, list) else [features]

    def audio_analysis(self, track_id: str) -> Dict[str, Any]:
        self.calls.append("audio_analysis")
        analyses = self._get("audio_analysis", {})
        return analyses.get(track_id, {}) if isinstance(analyses, dict) else analyses

    def current_user_top_tracks(self) -> Dict[str, Any]:
        self.calls.append("current_user_top_tracks")
        return self._get("current_user_top_tracks", {"items": []})

    def current_user_top_artists(self) -> Dict[str, Any]:
        self.calls.append("current_user_top_artists")
        return self._get("current_user_top_artists", {"items": []})

    def current_user_followed_artists(self) -> Dict[str, Any]:
        self.calls.append("current_user_followed_artists")
        return self._get(
            "current_user_followed_artists",
            {"artists": {"items": [], "next": None}},
        )

    def next(self, results: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        next_token = results.get("next")
        if next_token is None:
            return None
        next_payload = self._payload.get(next_token)
        return next_payload


@pytest.fixture
def fake_spotify_factory():
    """Factory fixture to build fake Spotify clients with custom payloads."""

    def _factory(**payload: Any) -> FakeSpotify:
        return FakeSpotify(**payload)

    return _factory


@pytest.fixture
def temp_database(monkeypatch, tmp_path):
    """Provide an isolated temporary SQLite database for each test."""
    from app import database as database_module

    db_file = tmp_path / "test.sqlite"
    database_url = f"sqlite:///{db_file}"
    manager = database_module.DatabaseManager(database_url)
    manager.create_tables()

    @contextmanager
    def session_override():
        with manager.session_scope() as session:
            yield session

    # Patch the database module to use the temporary manager
    monkeypatch.setattr(database_module, "db_manager", manager, raising=False)
    monkeypatch.setattr(database_module, "db_session", session_override, raising=False)

    # Ensure other modules import the patched session
    from app import data_access as data_access_module

    reload(data_access_module)
    monkeypatch.setattr(data_access_module, "db_session", session_override, raising=False)

    yield manager

    manager.drop_tables()


@pytest.fixture
def app_module(monkeypatch, temp_database):
    """Reload the Flask app with testing configuration and temp database."""
    monkeypatch.setenv("SPOTIFY_CLIENT_ID", "dummy")
    monkeypatch.setenv("SPOTIFY_CLIENT_SECRET", "dummy")
    monkeypatch.setenv("APP_SECRET_KEY", "testing-secret")

    from app import app as app_module

    reloaded = reload(app_module)
    reloaded.app.config.update({"TESTING": True})
    return reloaded


@pytest.fixture
def client(app_module):
    with app_module.app.test_client() as client:
        yield client


@pytest.fixture
def db_session_factory(temp_database):
    """Return a callable to create managed database sessions in tests."""
    from app.database import db_session

    def _factory():
        return db_session()

    return _factory
