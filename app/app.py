import os
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, request, session, url_for

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
    token = spotify.authorize_access_token()
    resp = spotify.get('me')
    profile = resp.json()
    # Do something with the profile, e.g., store in session or database
    return 'Logged in as ' + profile['id']

if __name__ == '__main__':
    app.run(debug=True)
