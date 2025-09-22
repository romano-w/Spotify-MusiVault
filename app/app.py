
"""Flask application factory and routes for Spotify MusiVault."""

from collections.abc import Mapping
import time
from typing import Any

import spotipy
from authlib.integrations.flask_client import OAuth
from dotenv import load_dotenv
from flask import Blueprint, Flask, current_app, redirect, request, session, url_for

from app.config import validate_required_settings
from app.data_access import SpotifyDataAccess
from app.database import db_session, init_database
from app.models import User
from app.spotify_api_services import (
    get_followed_artists,
    get_playlist,
    get_playlist_cover_image,
    get_playlist_items,
    get_saved_tracks,
    get_several_audio_features,
    get_several_tracks,
    get_track,
    get_track_audio_analysis,
    get_track_audio_features,
    get_user,
    get_user_playlists,
    get_user_top_items,
)
from app.spotify_utils import print_structure


bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return redirect(url_for("main.login"))


@bp.route("/login")
def login():
    spotify_oauth = current_app.extensions["spotify_oauth_client"]
    redirect_uri = url_for("main.authorize", _external=True)
    return spotify_oauth.authorize_redirect(redirect_uri)


@bp.route("/authorize")
def authorize():
    spotify_oauth = current_app.extensions["spotify_oauth_client"]
    token_info = spotify_oauth.authorize_access_token()
    if token_info is None:
        return redirect(url_for("main.login"))

    token_info = token_info.copy()
    if "expires_at" not in token_info:
        expires_in = token_info.get("expires_in")
        if expires_in is not None:
            token_info["expires_at"] = int(time.time()) + int(expires_in)

    session["spotify_token"] = token_info

    sp = spotipy.Spotify(auth=token_info["access_token"])

    fetch_and_print_spotify_data(sp)

    profile = sp.current_user()
    return "Logged in as " + profile["id"]


@bp.route("/user")
def user():
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    user_info = get_user(sp)
    return user_info


@bp.route("/user/playlists")
def user_playlists():
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    playlists = get_user_playlists(sp)
    return {"playlists": playlists}


@bp.route("/playlist/<playlist_id>")
def playlist(playlist_id):
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    playlist_info = get_playlist(sp, playlist_id)
    return playlist_info


@bp.route("/playlist/<playlist_id>/items")
def playlist_items(playlist_id):
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    items = get_playlist_items(sp, playlist_id)
    return {"items": items}


@bp.route("/playlist/<playlist_id>/cover")
def playlist_cover(playlist_id):
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    cover_image = get_playlist_cover_image(sp, playlist_id)
    return {"cover_image": cover_image}


@bp.route("/track/<track_id>")
def track(track_id):
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    track_info = get_track(sp, track_id)
    return track_info


@bp.route("/tracks")
def several_tracks():
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    track_ids = request.args.getlist("ids")
    tracks_info = get_several_tracks(sp, track_ids)
    return {"tracks": tracks_info}


@bp.route("/user/saved_tracks")
def saved_tracks():
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    tracks = get_saved_tracks(sp)
    return {"saved_tracks": tracks}


@bp.route("/audio_features")
def audio_features():
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    track_ids = request.args.getlist("ids")
    features = get_several_audio_features(sp, track_ids)
    return {"audio_features": features}


@bp.route("/track/<track_id>/audio_features")
def track_audio_features(track_id):
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    features = get_track_audio_features(sp, track_id)
    return {"audio_features": features}


@bp.route("/track/<track_id>/audio_analysis")
def track_audio_analysis(track_id):
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    analysis = get_track_audio_analysis(sp, track_id)
    return analysis


@bp.route("/user/top/<type>")
def user_top_items(type):
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    top_items = get_user_top_items(sp, type)
    return {"top_items": top_items}


@bp.route("/user/followed_artists")
def followed_artists():
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for("main.login"))
    artists = get_followed_artists(sp)
    return {"followed_artists": artists}


@bp.route("/db-test")
def test_database():
    """Test database connectivity and basic operations."""
    try:
        with db_session() as session_scope:
            user_count = session_scope.query(User).count()
            return {
                "status": "success",
                "message": "Database connection successful",
                "user_count": user_count,
            }
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {
            "status": "error",
            "message": f"Database error: {str(exc)}",
        }, 500


@bp.route("/db-stats")
def database_stats():
    """Get database statistics."""
    try:
        stats = SpotifyDataAccess.get_database_stats()
        return {
            "status": "success",
            "stats": stats,
        }
    except Exception as exc:  # pragma: no cover - diagnostic path
        return {
            "status": "error",
            "message": f"Error retrieving stats: {str(exc)}",
        }, 500


def create_spotify_client():
    spotify_oauth = current_app.extensions.get("spotify_oauth_client")
    if spotify_oauth is None:
        raise RuntimeError("Spotify OAuth client has not been configured on the app.")

    token_info = session.get("spotify_token")
    if not token_info:
        return None

    expires_at = token_info.get("expires_at")
    if expires_at is None:
        expires_in = token_info.get("expires_in")
        if expires_in is not None:
            expires_at = int(time.time()) + int(expires_in)
            token_info["expires_at"] = expires_at
            session["spotify_token"] = token_info

    if expires_at is not None and expires_at <= int(time.time()):
        refresh_token = token_info.get("refresh_token")
        if not refresh_token:
            session.pop("spotify_token", None)
            return None

        refreshed_token = spotify_oauth.refresh_token(
            spotify_oauth.access_token_url,
            refresh_token=refresh_token,
        )
        if "refresh_token" not in refreshed_token and refresh_token:
            refreshed_token["refresh_token"] = refresh_token
        if "expires_at" not in refreshed_token:
            expires_in = refreshed_token.get("expires_in")
            if expires_in is not None:
                refreshed_token["expires_at"] = int(time.time()) + int(expires_in)
        session["spotify_token"] = refreshed_token
        token_info = refreshed_token

    access_token = token_info.get("access_token")
    if not access_token:
        session.pop("spotify_token", None)
        return None

    return spotipy.Spotify(auth=access_token)


def fetch_and_print_spotify_data(sp):
    user_info = get_user(sp)
    print("User Info:", user_info)
    top_tracks = get_user_top_items(sp, "tracks")
    print_structure(top_tracks)


def _configure_app(app: Flask, config_object: Any = None) -> None:
    if config_object is not None:
        if isinstance(config_object, Mapping):
            app.config.update(config_object)
        else:
            app.config.from_object(config_object)


def create_app(config_object: Any = None) -> Flask:
    load_dotenv()
    app = Flask(__name__)

    _configure_app(app, config_object)

    validated = validate_required_settings(app.config)
    for key, value in validated.items():
        app.config.setdefault(key, value)

    app.secret_key = app.config["APP_SECRET_KEY"]

    oauth = OAuth(app)
    spotify_oauth = oauth.register(
        name="spotify",
        client_id=app.config["SPOTIFY_CLIENT_ID"],
        client_secret=app.config["SPOTIFY_CLIENT_SECRET"],
        access_token_url="https://accounts.spotify.com/api/token",
        access_token_params=None,
        authorize_url="https://accounts.spotify.com/authorize",
        authorize_params=None,
        api_base_url="https://api.spotify.com/v1/",
        client_kwargs={
            "scope": "playlist-read-private playlist-read-collaborative user-top-read user-follow-read user-library-read",
        },
    )
    app.extensions["spotify_oauth_client"] = spotify_oauth

    try:
        init_database()
        app.logger.info("Database ready!")
    except Exception as exc:  # pragma: no cover - diagnostic path
        app.logger.warning("Database initialization warning: %s", exc)

    app.register_blueprint(bp)
    return app


if __name__ == "__main__":
    application = create_app()
    application.run(debug=True)
