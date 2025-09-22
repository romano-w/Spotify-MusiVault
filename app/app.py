import os
import time
from typing import Optional

import spotipy
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth

from flask import Flask, redirect, request, session, url_for
from .spotify_api_services import (
    get_saved_tracks,
    get_several_audio_features,
    get_track_audio_analysis,
    get_track_audio_features,
    get_user,
    get_user_playlists,
    get_user_top_items,
    get_playlist_items,
)
from .database import init_database, db_session
from .models import User
from .data_access import SpotifyDataAccess

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize database on startup
try:
    init_database()
    print("Database ready!")
except Exception as e:
    print(f"Database initialization warning: {e}")

# Use the secret key from the .env file
app.secret_key = os.getenv('APP_SECRET_KEY')

oauth = OAuth(app)
spotify = oauth.register(
    name='spotify',
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    access_token_url='https://accounts.spotify.com/api/token',
    access_token_params=None,
    authorize_url='https://accounts.spotify.com/authorize',
    authorize_params=None,
    api_base_url='https://api.spotify.com/v1/',
    client_kwargs={'scope': 'playlist-read-private playlist-read-collaborative user-top-read user-follow-read user-library-read'},
)

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return spotify.authorize_redirect(redirect_uri)

@app.route('/authorize')
def authorize():
    token_info = spotify.authorize_access_token()
    if token_info is None:
        return redirect(url_for('login'))

    token_info = token_info.copy()
    if 'expires_at' not in token_info:
        expires_in = token_info.get('expires_in')
        if expires_in is not None:
            token_info['expires_at'] = int(time.time()) + int(expires_in)

    session['spotify_token'] = token_info

    sp = spotipy.Spotify(auth=token_info['access_token'])

    user_id = sync_spotify_data(sp)
    session['current_user_id'] = user_id

    return {'status': 'synchronized', 'user_id': user_id}

# @app.route('/authorize')
# def authorize():
#     token_info = spotify.authorize_access_token()
    
#     # Creating a Spotipy client with the access token
#     sp = spotipy.Spotify(auth=token_info['access_token'])

#     # Fetch and log the user's playlists
#     playlists = sp.current_user_playlists()
#     while playlists:
#         for i, playlist in enumerate(playlists['items']):
#             print(f"{i + playlists['offset']} - {playlist['name']}")
#         if playlists['next']:
#             playlists = sp.next(playlists)
#         else:
#             playlists = None
    
#     # Example of using a function from spotify_utils
#     playlists = get_playlist_items(sp, 'some_playlist_id')

#     profile = sp.current_user()
#     # Do something with the profile, e.g., store in session or database
#     return 'Logged in as ' + profile['id']

def _current_user_id() -> Optional[str]:
    return session.get('current_user_id')


@app.route('/user')
def user():
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    user_info = SpotifyDataAccess.get_user(user_id)
    if not user_info:
        return {'error': 'User not found'}, 404
    return {'user': user_info}


@app.route('/user/playlists')
def user_playlists():
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    playlists = SpotifyDataAccess.get_user_playlists(user_id)
    return {'playlists': playlists}


@app.route('/playlist/<playlist_id>')
def playlist(playlist_id):
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    playlist_info = SpotifyDataAccess.get_playlist(playlist_id)
    if not playlist_info:
        return {'error': 'Playlist not found'}, 404
    if playlist_info.get('owner_id') != user_id:
        return {'error': 'Playlist not accessible'}, 403
    return playlist_info


@app.route('/playlist/<playlist_id>/items')
def playlist_items(playlist_id):
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    playlist_info = SpotifyDataAccess.get_playlist(playlist_id)
    if not playlist_info:
        return {'error': 'Playlist not found'}, 404
    if playlist_info.get('owner_id') != user_id:
        return {'error': 'Playlist not accessible'}, 403
    return {'items': playlist_info.get('tracks', [])}


@app.route('/playlist/<playlist_id>/cover')
def playlist_cover(playlist_id):
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    playlist_info = SpotifyDataAccess.get_playlist(playlist_id)
    if not playlist_info:
        return {'error': 'Playlist not found'}, 404
    if playlist_info.get('owner_id') != user_id:
        return {'error': 'Playlist not accessible'}, 403
    return {'images': playlist_info.get('images', [])}


@app.route('/track/<track_id>')
def track(track_id):
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    track_info = SpotifyDataAccess.get_track(track_id)
    if not track_info:
        return {'error': 'Track not found'}, 404
    return track_info


@app.route('/tracks')
def several_tracks():
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    track_ids = request.args.getlist('ids')
    tracks_info = SpotifyDataAccess.get_tracks(track_ids)
    return {'tracks': tracks_info}


@app.route('/user/saved_tracks')
def saved_tracks():
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    tracks = SpotifyDataAccess.get_saved_tracks(user_id)
    return {'saved_tracks': tracks}


@app.route('/audio_features')
def audio_features():
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for('login'))
    track_ids = request.args.getlist('ids')
    features = get_several_audio_features(sp, track_ids)
    return {'audio_features': features}


@app.route('/track/<track_id>/audio_features')
def track_audio_features(track_id):
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for('login'))
    features = get_track_audio_features(sp, track_id)
    return {'audio_features': features}


@app.route('/track/<track_id>/audio_analysis')
def track_audio_analysis(track_id):
    sp = create_spotify_client()
    if sp is None:
        return redirect(url_for('login'))
    analysis = get_track_audio_analysis(sp, track_id)
    return analysis


@app.route('/user/top/<type>')
def user_top_items(type):
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    time_range = request.args.get('time_range')
    if type == 'tracks':
        top_items = SpotifyDataAccess.get_user_top_tracks(user_id, time_range)
    elif type == 'artists':
        top_items = SpotifyDataAccess.get_user_top_artists(user_id, time_range)
    else:
        return {'error': 'Invalid type'}, 400
    return {'top_items': top_items}


@app.route('/user/followed_artists')
def followed_artists():
    user_id = _current_user_id()
    if not user_id:
        return redirect(url_for('login'))
    # Followed artists are not yet persisted locally.
    return {'followed_artists': []}

def create_spotify_client():
    token_info = session.get('spotify_token')
    if not token_info:
        return None

    expires_at = token_info.get('expires_at')
    if expires_at is None:
        expires_in = token_info.get('expires_in')
        if expires_in is not None:
            expires_at = int(time.time()) + int(expires_in)
            token_info['expires_at'] = expires_at
            session['spotify_token'] = token_info

    if expires_at is not None and expires_at <= int(time.time()):
        refresh_token = token_info.get('refresh_token')
        if not refresh_token:
            session.pop('spotify_token', None)
            return None

        refreshed_token = spotify.refresh_token(
            spotify.access_token_url,
            refresh_token=refresh_token,
        )
        if 'refresh_token' not in refreshed_token and refresh_token:
            refreshed_token['refresh_token'] = refresh_token
        if 'expires_at' not in refreshed_token:
            expires_in = refreshed_token.get('expires_in')
            if expires_in is not None:
                refreshed_token['expires_at'] = int(time.time()) + int(expires_in)
        session['spotify_token'] = refreshed_token
        token_info = refreshed_token

    access_token = token_info.get('access_token')
    if not access_token:
        session.pop('spotify_token', None)
        return None

    return spotipy.Spotify(auth=access_token)

def sync_spotify_data(sp):
    """Fetch data from Spotify and persist it to the local database."""

    user_info = get_user(sp)
    playlists_payload = []
    for playlist in get_user_playlists(sp):
        playlist_id = playlist.get('id')
        if not playlist_id:
            continue
        items = get_playlist_items(sp, playlist_id)
        playlists_payload.append({'playlist': playlist, 'items': items})

    saved_tracks = get_saved_tracks(sp)
    top_tracks = get_user_top_items(sp, 'tracks')
    top_artists = get_user_top_items(sp, 'artists')

    return SpotifyDataAccess.store_user_snapshot(
        user_info,
        playlists=playlists_payload,
        saved_tracks=saved_tracks,
        top_tracks=top_tracks,
        top_artists=top_artists,
    )

@app.route('/db-test')
def test_database():
    """Test database connectivity and basic operations."""
    try:
        with db_session() as session:
            # Try to query users table
            user_count = session.query(User).count()
            return {
                'status': 'success',
                'message': 'Database connection successful',
                'user_count': user_count
            }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Database error: {str(e)}'
        }, 500

@app.route('/db-stats')
def database_stats():
    """Get database statistics."""
    try:
        stats = SpotifyDataAccess.get_database_stats()
        return {
            'status': 'success',
            'stats': stats
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error retrieving stats: {str(e)}'
        }, 500

if __name__ == '__main__':
    app.run(debug=True)
