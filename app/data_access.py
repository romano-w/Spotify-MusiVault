"""
Data Access Layer (DAL) for Spotify MusiVault.
Provides high-level database operations for Spotify data.
"""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Type

from sqlalchemy.orm import Session, joinedload

from .models import (
    Album,
    Artist,
    AudioFeatures,
    Playlist,
    SavedTrack,
    Track,
    User,
    UserTopArtist,
    UserTopTrack,
)
from .database import db_session
from .serializers import (
    serialize_artist,
    serialize_playlist,
    serialize_saved_track,
    serialize_track,
    serialize_user,
    serialize_user_top_artist,
    serialize_user_top_track,
)


def _safe_json_dumps(value: Any) -> str:
    """Serialize Python structures to JSON stored in the DB."""
    if value is None:
        return json.dumps([])
    if isinstance(value, (dict, list)):
        return json.dumps(value)
    return json.dumps(value)


def _parse_datetime(value: Optional[str]) -> Optional[datetime]:
    """Parse Spotify timestamps into timezone-aware datetimes."""
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def _get_from_identity_map(session: Session, model: Type[Any], pk: Any):
    """Fetch an instance from the session identity map when available."""
    identity_key = session.identity_key(model, pk)
    return session.identity_map.get(identity_key)


def _find_pending_instance(session: Session, model: Type[Any], pk: Any):
    """Return a pending instance matching the given primary key."""
    primary_keys = model.__mapper__.primary_key
    if len(primary_keys) != 1:
        return None
    key_name = primary_keys[0].key
    for instance in session.new:
        if isinstance(instance, model) and getattr(instance, key_name) == pk:
            return instance
    return None


class SpotifyDataAccess:
    """Data access operations for Spotify entities."""

    # ------------------------------------------------------------------
    # Upsert helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_user(session: Session, user_data: Dict[str, Any]) -> User:
        user = session.get(User, user_data["id"])

        if not user:
            user = User(id=user_data["id"])
            session.add(user)

        user.display_name = user_data.get("display_name")
        user.email = user_data.get("email")
        user.country = user_data.get("country")
        user.followers_total = user_data.get("followers", {}).get("total", 0)
        user.spotify_url = user_data.get("external_urls", {}).get("spotify")
        user.href = user_data.get("href")
        user.uri = user_data.get("uri")
        user.product = user_data.get("product")
        user.updated_at = datetime.utcnow()

        return user

    @staticmethod
    def _ensure_artist(session: Session, artist_data: Dict[str, Any]) -> Optional[Artist]:
        artist_id = artist_data.get("id")
        if not artist_id:
            return None

        artist = (
            _get_from_identity_map(session, Artist, artist_id)
            or _find_pending_instance(session, Artist, artist_id)
            or session.get(Artist, artist_id)
        )
        if not artist:
            artist = Artist(id=artist_id)
            session.add(artist)

        artist.name = artist_data.get("name")
        artist.genres = _safe_json_dumps(artist_data.get("genres", []))
        artist.popularity = artist_data.get("popularity")
        artist.followers_total = artist_data.get("followers", {}).get("total", 0)
        artist.spotify_url = artist_data.get("external_urls", {}).get("spotify")
        artist.href = artist_data.get("href")
        artist.uri = artist_data.get("uri")
        artist.images = _safe_json_dumps(artist_data.get("images", []))
        artist.updated_at = datetime.utcnow()
        return artist

    @staticmethod
    def _ensure_album(session: Session, album_data: Dict[str, Any]) -> Optional[Album]:
        album_id = album_data.get("id")
        if not album_id:
            return None

        album = (
            _get_from_identity_map(session, Album, album_id)
            or _find_pending_instance(session, Album, album_id)
            or session.get(Album, album_id)
        )
        if not album:
            album = Album(id=album_id)
            session.add(album)

        album.name = album_data.get("name")
        album.album_type = album_data.get("album_type")
        album.total_tracks = album_data.get("total_tracks")
        album.release_date = album_data.get("release_date")
        album.release_date_precision = album_data.get("release_date_precision")
        album.available_markets = _safe_json_dumps(album_data.get("available_markets", []))
        album.spotify_url = album_data.get("external_urls", {}).get("spotify")
        album.href = album_data.get("href")
        album.uri = album_data.get("uri")
        album.images = _safe_json_dumps(album_data.get("images", []))
        album.label = album_data.get("label")
        album.popularity = album_data.get("popularity")
        album.updated_at = datetime.utcnow()

        album_artists = []
        for artist_data in album_data.get("artists", []):
            artist = SpotifyDataAccess._ensure_artist(session, artist_data)
            if artist:
                album_artists.append(artist)
        if album_artists:
            album.artists = album_artists

        return album

    @staticmethod
    def _ensure_track(session: Session, track_data: Dict[str, Any]) -> Optional[Track]:
        track_id = track_data.get("id")
        if not track_id:
            return None

        track = (
            _get_from_identity_map(session, Track, track_id)
            or _find_pending_instance(session, Track, track_id)
            or session.get(Track, track_id)
        )
        if not track:
            track = Track(id=track_id)
            session.add(track)

        track.name = track_data.get("name")
        track.duration_ms = track_data.get("duration_ms")
        track.explicit = track_data.get("explicit", False)
        track.popularity = track_data.get("popularity")
        track.preview_url = track_data.get("preview_url")
        track.track_number = track_data.get("track_number")
        track.disc_number = track_data.get("disc_number", 1)
        track.is_local = track_data.get("is_local", False)
        track.available_markets = _safe_json_dumps(track_data.get("available_markets", []))
        track.spotify_url = track_data.get("external_urls", {}).get("spotify")
        track.href = track_data.get("href")
        track.uri = track_data.get("uri")
        track.external_ids = _safe_json_dumps(track_data.get("external_ids", {}))
        track.updated_at = datetime.utcnow()

        album_data = track_data.get("album")
        if album_data:
            album = SpotifyDataAccess._ensure_album(session, album_data)
            if album:
                track.album = album

        artist_entities = []
        for artist_data in track_data.get("artists", []):
            artist = SpotifyDataAccess._ensure_artist(session, artist_data)
            if artist:
                artist_entities.append(artist)
        if artist_entities:
            track.artists = artist_entities

        return track

    # ------------------------------------------------------------------
    # Public upsert helpers
    # ------------------------------------------------------------------

    @staticmethod
    def create_or_update_user(user_data: Dict[str, Any]) -> Dict[str, Any]:
        with db_session() as session:
            user = SpotifyDataAccess._ensure_user(session, user_data)
            session.flush()
            return serialize_user(user)

    @staticmethod
    def create_or_update_artist(artist_data: Dict[str, Any]) -> Dict[str, Any]:
        with db_session() as session:
            artist = SpotifyDataAccess._ensure_artist(session, artist_data)
            session.flush()
            return serialize_artist(artist) if artist else {}

    @staticmethod
    def create_or_update_album(album_data: Dict[str, Any]) -> Optional[Album]:
        with db_session() as session:
            album = SpotifyDataAccess._ensure_album(session, album_data)
            session.flush()
            return album

    @staticmethod
    def create_or_update_track(track_data: Dict[str, Any], album_id: Optional[str] = None) -> Dict[str, Any]:
        with db_session() as session:
            if album_id and "album" not in track_data:
                track_data = dict(track_data)
                track_data["album"] = {"id": album_id}
            track = SpotifyDataAccess._ensure_track(session, track_data)
            session.flush()
            return serialize_track(track) if track else {}

    @staticmethod
    def create_or_update_playlist(playlist_data: Dict[str, Any], owner_id: str) -> Playlist:
        with db_session() as session:
            playlist = SpotifyDataAccess._ensure_playlist(session, playlist_data, owner_id)
            session.flush()
            return playlist

    # ------------------------------------------------------------------
    # Snapshot storage
    # ------------------------------------------------------------------

    @staticmethod
    def _ensure_playlist(session: Session, playlist_data: Dict[str, Any], owner_id: str) -> Playlist:
        playlist_id = playlist_data["id"]
        playlist = session.get(Playlist, playlist_id)
        if not playlist:
            playlist = Playlist(id=playlist_id, owner_id=owner_id)
            session.add(playlist)

        playlist.name = playlist_data.get("name")
        playlist.description = playlist_data.get("description")
        playlist.public = playlist_data.get("public")
        playlist.collaborative = playlist_data.get("collaborative", False)
        playlist.followers_total = playlist_data.get("followers", {}).get("total", 0)
        playlist.snapshot_id = playlist_data.get("snapshot_id")
        playlist.spotify_url = playlist_data.get("external_urls", {}).get("spotify")
        playlist.href = playlist_data.get("href")
        playlist.uri = playlist_data.get("uri")
        playlist.images = _safe_json_dumps(playlist_data.get("images", []))
        playlist.primary_color = playlist_data.get("primary_color")
        playlist.updated_at = datetime.utcnow()
        playlist.owner_id = owner_id
        return playlist

    @staticmethod
    def _extract_time_range(top_payload: Any, default: str = "medium_term") -> str:
        if isinstance(top_payload, dict):
            if "time_range" in top_payload:
                return top_payload["time_range"]
            href = top_payload.get("href")
            if href and "time_range=" in href:
                return href.split("time_range=")[1].split("&")[0]
        return default

    @staticmethod
    def store_user_snapshot(
        user_data: Dict[str, Any],
        playlists: Optional[Iterable[Dict[str, Any]]] = None,
        saved_tracks: Optional[Iterable[Dict[str, Any]]] = None,
        top_tracks: Optional[Any] = None,
        top_artists: Optional[Any] = None,
    ) -> str:
        """Persist the current Spotify snapshot for a user."""

        playlists = playlists or []
        saved_tracks = saved_tracks or []

        with db_session() as session:
            user = SpotifyDataAccess._ensure_user(session, user_data)
            session.flush()

            SpotifyDataAccess._store_playlists(session, user, playlists)
            session.flush()
            SpotifyDataAccess._store_saved_tracks(session, user, saved_tracks)
            session.flush()
            SpotifyDataAccess._store_top_tracks(session, user, top_tracks)
            SpotifyDataAccess._store_top_artists(session, user, top_artists)

            return user.id

    @staticmethod
    def _store_playlists(session: Session, user: User, playlists: Iterable[Dict[str, Any]]) -> None:
        playlist_entities: List[Playlist] = []
        for payload in playlists:
            if "playlist" in payload:
                playlist_data = payload.get("playlist", {})
                items = payload.get("items", [])
            else:
                playlist_data = payload
                items = []

            if "id" not in playlist_data:
                continue

            playlist = SpotifyDataAccess._ensure_playlist(session, playlist_data, user.id)
            SpotifyDataAccess._store_playlist_items(session, playlist, items)
            playlist_entities.append(playlist)

        # Keep relationships consistent for SQLAlchemy session
        if playlist_entities:
            user.playlists = playlist_entities

    @staticmethod
    def _store_playlist_items(session: Session, playlist: Playlist, items: Iterable[Dict[str, Any]]) -> None:
        tracks: List[Track] = []
        for item in items or []:
            track_data = item.get("track") if isinstance(item, dict) else None
            if not track_data:
                continue
            track = SpotifyDataAccess._ensure_track(session, track_data)
            if track:
                tracks.append(track)
        if tracks:
            playlist.tracks = tracks
        else:
            playlist.tracks = []

    @staticmethod
    def _store_saved_tracks(session: Session, user: User, saved_tracks: Iterable[Dict[str, Any]]) -> None:
        session.query(SavedTrack).filter(SavedTrack.user_id == user.id).delete()
        for item in saved_tracks or []:
            track_data = item.get("track") if isinstance(item, dict) else None
            if not track_data:
                continue
            track = SpotifyDataAccess._ensure_track(session, track_data)
            if not track:
                continue
            added_at = _parse_datetime(item.get("added_at"))
            saved_track = SavedTrack(user_id=user.id, track_id=track.id, added_at=added_at or datetime.utcnow())
            session.add(saved_track)

    @staticmethod
    def _store_top_tracks(session: Session, user: User, payload: Any) -> None:
        if payload is None:
            session.query(UserTopTrack).filter(UserTopTrack.user_id == user.id).delete()
            return

        items = payload.get("items") if isinstance(payload, dict) else payload
        if items is None:
            items = []
        time_range = SpotifyDataAccess._extract_time_range(payload)
        session.query(UserTopTrack).filter(
            UserTopTrack.user_id == user.id, UserTopTrack.time_range == time_range
        ).delete()

        for index, item in enumerate(items, start=1):
            track = SpotifyDataAccess._ensure_track(session, item)
            if not track:
                continue
            top_entry = UserTopTrack(
                user_id=user.id,
                track_id=track.id,
                time_range=time_range,
                rank=index,
            )
            session.add(top_entry)

    @staticmethod
    def _store_top_artists(session: Session, user: User, payload: Any) -> None:
        if payload is None:
            session.query(UserTopArtist).filter(UserTopArtist.user_id == user.id).delete()
            return

        items = payload.get("items") if isinstance(payload, dict) else payload
        if items is None:
            items = []
        time_range = SpotifyDataAccess._extract_time_range(payload)
        session.query(UserTopArtist).filter(
            UserTopArtist.user_id == user.id, UserTopArtist.time_range == time_range
        ).delete()

        for index, item in enumerate(items, start=1):
            artist = SpotifyDataAccess._ensure_artist(session, item)
            if not artist:
                continue
            top_entry = UserTopArtist(
                user_id=user.id,
                artist_id=artist.id,
                time_range=time_range,
                rank=index,
            )
            session.add(top_entry)

    # ------------------------------------------------------------------
    # Retrieval helpers
    # ------------------------------------------------------------------

    @staticmethod
    def get_user(user_id: str) -> Optional[dict]:
        with db_session() as session:
            user = session.get(User, user_id)
            if not user:
                return None
            return serialize_user(user)

    @staticmethod
    def get_user_playlists(user_id: str) -> List[dict]:
        with db_session() as session:
            playlists = (
                session.query(Playlist)
                .options(
                    joinedload(Playlist.tracks)
                    .joinedload(Track.artists),
                    joinedload(Playlist.tracks).joinedload(Track.album),
                )
                .filter(Playlist.owner_id == user_id)
                .all()
            )
            return [serialize_playlist(p, include_tracks=True) for p in playlists]

    @staticmethod
    def get_playlist(playlist_id: str) -> Optional[dict]:
        with db_session() as session:
            playlist = (
                session.query(Playlist)
                .options(
                    joinedload(Playlist.tracks)
                    .joinedload(Track.artists),
                    joinedload(Playlist.tracks).joinedload(Track.album),
                )
                .filter(Playlist.id == playlist_id)
                .first()
            )
            if not playlist:
                return None
            return serialize_playlist(playlist, include_tracks=True)

    @staticmethod
    def get_saved_tracks(user_id: str) -> List[dict]:
        with db_session() as session:
            saved_tracks = (
                session.query(SavedTrack)
                .options(
                    joinedload(SavedTrack.track).joinedload(Track.album),
                    joinedload(SavedTrack.track).joinedload(Track.artists),
                )
                .filter(SavedTrack.user_id == user_id)
                .order_by(SavedTrack.added_at.desc())
                .all()
            )
            return [serialize_saved_track(st) for st in saved_tracks]

    @staticmethod
    def get_user_top_tracks(user_id: str, time_range: Optional[str] = None) -> List[dict]:
        with db_session() as session:
            query = (
                session.query(UserTopTrack)
                .options(
                    joinedload(UserTopTrack.track).joinedload(Track.album),
                    joinedload(UserTopTrack.track).joinedload(Track.artists),
                )
                .filter(UserTopTrack.user_id == user_id)
            )
            if time_range:
                query = query.filter(UserTopTrack.time_range == time_range)
            entries = query.order_by(UserTopTrack.time_range, UserTopTrack.rank).all()
            return [serialize_user_top_track(entry) for entry in entries]

    @staticmethod
    def get_user_top_artists(user_id: str, time_range: Optional[str] = None) -> List[dict]:
        with db_session() as session:
            query = (
                session.query(UserTopArtist)
                .options(joinedload(UserTopArtist.artist))
                .filter(UserTopArtist.user_id == user_id)
            )
            if time_range:
                query = query.filter(UserTopArtist.time_range == time_range)
            entries = query.order_by(UserTopArtist.time_range, UserTopArtist.rank).all()
            return [serialize_user_top_artist(entry) for entry in entries]

    @staticmethod
    def get_track(track_id: str) -> Optional[dict]:
        with db_session() as session:
            track = (
                session.query(Track)
                .options(joinedload(Track.album), joinedload(Track.artists))
                .filter(Track.id == track_id)
                .first()
            )
            if not track:
                return None
            return serialize_track(track)

    @staticmethod
    def get_tracks(track_ids: Iterable[str]) -> List[dict]:
        ids = list(track_ids)
        if not ids:
            return []
        with db_session() as session:
            tracks = (
                session.query(Track)
                .options(joinedload(Track.album), joinedload(Track.artists))
                .filter(Track.id.in_(ids))
                .all()
            )
            tracks_by_id = {track.id: track for track in tracks}
            return [serialize_track(tracks_by_id[track_id]) for track_id in ids if track_id in tracks_by_id]

    @staticmethod
    def get_database_stats() -> Dict[str, int]:
        with db_session() as session:
            return {
                "users": session.query(User).count(),
                "artists": session.query(Artist).count(),
                "albums": session.query(Album).count(),
                "tracks": session.query(Track).count(),
                "playlists": session.query(Playlist).count(),
                "audio_features": session.query(AudioFeatures).count(),
                "saved_tracks": session.query(SavedTrack).count(),
            }
