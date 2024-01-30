import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, request, session, url_for
from spotify_utils import (
    get_user, get_user_playlists, get_playlist, get_playlist_items,
    get_playlist_cover_image, get_track, get_several_tracks, get_saved_tracks,
    get_several_audio_features, get_track_audio_features,
    get_track_audio_analysis, get_user_top_items, get_followed_artists
)

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

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
    
    # Creating a Spotipy client with the access token
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Fetch and log the user's playlists
    playlists = sp.current_user_playlists()
    while playlists:
        for i, playlist in enumerate(playlists['items']):
            print(f"{i + playlists['offset']} - {playlist['name']}")
        if playlists['next']:
            playlists = sp.next(playlists)
        else:
            playlists = None
    
    # Example of using a function from spotify_utils
    playlists = get_playlist_items(sp, 'some_playlist_id')

    profile = sp.current_user()
    # Do something with the profile, e.g., store in session or database
    return 'Logged in as ' + profile['id']

@app.route('/user')
def user():
    sp = create_spotify_client()
    user_info = get_user(sp)
    return user_info

@app.route('/user/playlists')
def user_playlists():
    sp = create_spotify_client()
    playlists = get_user_playlists(sp)
    return {"playlists": playlists}

@app.route('/playlist/<playlist_id>')
def playlist(playlist_id):
    sp = create_spotify_client()
    playlist_info = get_playlist(sp, playlist_id)
    return playlist_info

@app.route('/playlist/<playlist_id>/items')
def playlist_items(playlist_id):
    sp = create_spotify_client()
    items = get_playlist_items(sp, playlist_id)
    return {"items": items}

@app.route('/playlist/<playlist_id>/cover')
def playlist_cover(playlist_id):
    sp = create_spotify_client()
    cover_image = get_playlist_cover_image(sp, playlist_id)
    return {"cover_image": cover_image}

@app.route('/track/<track_id>')
def track(track_id):
    sp = create_spotify_client()
    track_info = get_track(sp, track_id)
    return track_info

@app.route('/tracks')
def several_tracks():
    sp = create_spotify_client()
    # Assuming track IDs are passed as query parameters
    track_ids = request.args.getlist('ids')
    tracks_info = get_several_tracks(sp, track_ids)
    return {"tracks": tracks_info}

@app.route('/user/saved_tracks')
def saved_tracks():
    sp = create_spotify_client()
    tracks = get_saved_tracks(sp)
    return {"saved_tracks": tracks}

@app.route('/audio_features')
def audio_features():
    sp = create_spotify_client()
    # Assuming track IDs are passed as query parameters
    track_ids = request.args.getlist('ids')
    features = get_several_audio_features(sp, track_ids)
    return {"audio_features": features}

@app.route('/track/<track_id>/audio_features')
def track_audio_features(track_id):
    sp = create_spotify_client()
    features = get_track_audio_features(sp, track_id)
    return {"audio_features": features}

@app.route('/track/<track_id>/audio_analysis')
def track_audio_analysis(track_id):
    sp = create_spotify_client()
    analysis = get_track_audio_analysis(sp, track_id)
    return analysis

@app.route('/user/top/<type>')
def user_top_items(type):
    sp = create_spotify_client()
    top_items = get_user_top_items(sp, type)
    return {"top_items": top_items}

@app.route('/user/followed_artists')
def followed_artists():
    sp = create_spotify_client()
    artists = get_followed_artists(sp)
    return {"followed_artists": artists}

def create_spotify_client():
    token_info = spotify.authorize_access_token()
    return spotipy.Spotify(auth=token_info['access_token'])

if __name__ == '__main__':
    app.run(debug=True)
