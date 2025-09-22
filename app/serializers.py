"""Serialization helpers for converting ORM objects into JSON-ready dicts."""

from __future__ import annotations

import json
from typing import Any, Dict, Iterable, List, Optional

from .models import Album, Artist, Playlist, SavedTrack, Track, User, UserTopArtist, UserTopTrack


def _deserialize_json(value: Optional[str], default: Any) -> Any:
    if value is None:
        return default
    try:
        return json.loads(value)
    except (TypeError, json.JSONDecodeError):
        return default


def serialize_user(user: User) -> Dict[str, Any]:
    return {
        "id": user.id,
        "display_name": user.display_name,
        "email": user.email,
        "country": user.country,
        "followers_total": user.followers_total,
        "spotify_url": user.spotify_url,
        "href": user.href,
        "uri": user.uri,
        "product": user.product,
    }


def serialize_artist(artist: Artist) -> Dict[str, Any]:
    return {
        "id": artist.id,
        "name": artist.name,
        "genres": _deserialize_json(artist.genres, []),
        "popularity": artist.popularity,
        "followers_total": artist.followers_total,
        "spotify_url": artist.spotify_url,
        "href": artist.href,
        "uri": artist.uri,
        "images": _deserialize_json(artist.images, []),
    }


def serialize_album(album: Album) -> Dict[str, Any]:
    return {
        "id": album.id,
        "name": album.name,
        "album_type": album.album_type,
        "total_tracks": album.total_tracks,
        "release_date": album.release_date,
        "release_date_precision": album.release_date_precision,
        "available_markets": _deserialize_json(album.available_markets, []),
        "spotify_url": album.spotify_url,
        "href": album.href,
        "uri": album.uri,
        "images": _deserialize_json(album.images, []),
        "label": album.label,
        "popularity": album.popularity,
        "artists": [serialize_artist(artist) for artist in album.artists],
    }


def serialize_track(track: Track) -> Dict[str, Any]:
    return {
        "id": track.id,
        "name": track.name,
        "duration_ms": track.duration_ms,
        "explicit": track.explicit,
        "popularity": track.popularity,
        "preview_url": track.preview_url,
        "track_number": track.track_number,
        "disc_number": track.disc_number,
        "is_local": track.is_local,
        "available_markets": _deserialize_json(track.available_markets, []),
        "spotify_url": track.spotify_url,
        "href": track.href,
        "uri": track.uri,
        "external_ids": _deserialize_json(track.external_ids, {}),
        "album": serialize_album(track.album) if track.album else None,
        "artists": [serialize_artist(artist) for artist in track.artists],
    }


def serialize_playlist(playlist: Playlist, include_tracks: bool = False) -> Dict[str, Any]:
    data = {
        "id": playlist.id,
        "name": playlist.name,
        "description": playlist.description,
        "public": playlist.public,
        "collaborative": playlist.collaborative,
        "followers_total": playlist.followers_total,
        "snapshot_id": playlist.snapshot_id,
        "spotify_url": playlist.spotify_url,
        "href": playlist.href,
        "uri": playlist.uri,
        "images": _deserialize_json(playlist.images, []),
        "primary_color": playlist.primary_color,
        "owner_id": playlist.owner_id,
    }
    if include_tracks:
        data["tracks"] = [serialize_track(track) for track in playlist.tracks]
    return data


def serialize_saved_track(saved_track: SavedTrack) -> Dict[str, Any]:
    return {
        "id": saved_track.id,
        "user_id": saved_track.user_id,
        "track": serialize_track(saved_track.track) if saved_track.track else None,
        "added_at": saved_track.added_at.isoformat() if saved_track.added_at else None,
    }


def serialize_user_top_track(entry: UserTopTrack) -> Dict[str, Any]:
    return {
        "id": entry.id,
        "user_id": entry.user_id,
        "time_range": entry.time_range,
        "rank": entry.rank,
        "track": serialize_track(entry.track) if entry.track else None,
    }


def serialize_user_top_artist(entry: UserTopArtist) -> Dict[str, Any]:
    return {
        "id": entry.id,
        "user_id": entry.user_id,
        "time_range": entry.time_range,
        "rank": entry.rank,
        "artist": serialize_artist(entry.artist) if entry.artist else None,
    }


__all__ = [
    "serialize_album",
    "serialize_artist",
    "serialize_playlist",
    "serialize_saved_track",
    "serialize_track",
    "serialize_user",
    "serialize_user_top_artist",
    "serialize_user_top_track",
]
