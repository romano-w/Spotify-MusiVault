import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, request, session, url_for
from spotify_utils import get_user, get_user_playlists, get_playlist, \
    get_playlist_items, get_playlist_cover_image, get_track, \
    get_several_tracks, get_saved_tracks, get_several_audio_features, \
    get_track_audio_features, get_track_audio_analysis, get_user_top_items, \
    get_followed_artists

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
    client_kwargs={'scope': 'playlist-read-private'},
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

if __name__ == '__main__':
    app.run(debug=True)
