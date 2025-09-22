#!/usr/bin/env python3
"""
Fixed Flask app with proper imports
"""
import os
import sys
import spotipy
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, request, url_for, session

# Add app directory to path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

# Import our modules
from spotify_api_services import (
    get_user, get_user_playlists, get_playlist, get_playlist_items,
    get_playlist_cover_image, get_track, get_several_tracks, get_saved_tracks,
    get_several_audio_features, get_track_audio_features,
    get_track_audio_analysis, get_user_top_items, get_followed_artists,
)
from spotify_utils import (
    print_playlist_structure, print_playlist_items_structure, print_cover_image_structure, print_structure
)
from database import init_database, db_session
from models import User
from data_access import SpotifyDataStorage
from data_collector import SpotifyDataCollector

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Initialize database on startup
try:
    init_database()
    print("✅ Database ready!")
except Exception as e:
    print(f"⚠️  Database initialization warning: {e}")

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
    return '''
    <html>
    <head>
        <title>🎵 Spotify MusiVault</title>
        <style>
            body { font-family: Arial, sans-serif; text-align: center; padding: 50px; background: linear-gradient(135deg, #1DB954, #191414); color: white; }
            .container { max-width: 500px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; }
            .btn { background: #1DB954; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px; font-size: 18px; display: inline-block; margin: 20px; }
            .btn:hover { background: #1ed760; }
            h1 { font-size: 2.5em; margin-bottom: 30px; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 Spotify MusiVault</h1>
            <p>Collect and analyze your Spotify data!</p>
            <p>This will gather your:</p>
            <ul style="text-align: left; display: inline-block;">
                <li>🎵 All your playlists and tracks</li>
                <li>❤️ Saved tracks (liked songs)</li>
                <li>🎤 Top artists and tracks</li>
                <li>🎼 Audio features and analysis</li>
                <li>👤 Profile information</li>
            </ul>
            <br>
            <a href="/authorize" class="btn">🎯 Login with Spotify</a>
        </div>
    </body>
    </html>
    '''

@app.route('/authorize')
def authorize():
    try:
        # Get authorization from Spotify
        redirect_uri = url_for('callback', _external=True)
        return spotify.authorize_redirect(redirect_uri)
    except Exception as e:
        return f'<h1>❌ Authorization Error</h1><p>{str(e)}</p><a href="/">Try Again</a>'

@app.route('/callback')
def callback():
    try:
        # Handle the callback from Spotify
        token = spotify.authorize_access_token()
        session['token'] = token
        
        # Create Spotipy client
        sp = spotipy.Spotify(auth=token['access_token'])
        
        print("🎯 Starting data collection...")
        
        # Initialize data collector
        collector = SpotifyDataCollector(sp)
        
        # Collect all user data
        collection_result = collector.collect_all_user_data()
        
        print("✅ Data collection complete!")
        
        # Get database statistics
        database_stats = SpotifyDataStorage.get_database_stats()
        
        # Return success page with statistics
        return f'''
        <html>
        <head>
            <title>🎉 Collection Complete - Spotify MusiVault</title>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; padding: 30px; background: linear-gradient(135deg, #1DB954, #191414); color: white; }}
                .container {{ max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; }}
                .success {{ background: #1DB954; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .stats {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0; text-align: left; }}
                .stat-item {{ padding: 5px 0; border-bottom: 1px solid rgba(255,255,255,0.2); }}
                .btn {{ background: #1DB954; color: white; padding: 10px 20px; text-decoration: none; border-radius: 20px; margin: 10px; display: inline-block; }}
                .btn:hover {{ background: #1ed760; }}
                h1 {{ font-size: 2.5em; margin-bottom: 20px; }}
                h2 {{ color: #1DB954; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success">
                    <h1>🎉 Data Collection Complete!</h1>
                    <p>Your Spotify data has been successfully collected and stored!</p>
                </div>
                
                <h2>📊 Collection Results:</h2>
                <div class="stats">
                    <div class="stat-item"><strong>👤 Users stored:</strong> {database_stats.get('users', 0)}</div>
                    <div class="stat-item"><strong>🎤 Artists stored:</strong> {database_stats.get('artists', 0)}</div>
                    <div class="stat-item"><strong>💿 Albums stored:</strong> {database_stats.get('albums', 0)}</div>
                    <div class="stat-item"><strong>🎵 Tracks stored:</strong> {database_stats.get('tracks', 0)}</div>
                    <div class="stat-item"><strong>📝 Playlists stored:</strong> {database_stats.get('playlists', 0)}</div>
                    <div class="stat-item"><strong>🎼 Audio Features stored:</strong> {database_stats.get('audio_features', 0)}</div>
                    <div class="stat-item"><strong>🔗 Track-Artist links:</strong> {database_stats.get('track_artists', 0)}</div>
                    <div class="stat-item"><strong>📋 Playlist-Track links:</strong> {database_stats.get('playlist_tracks', 0)}</div>
                </div>
                
                <h2>✨ What's Next?</h2>
                <p>Your data is now stored in the local database. You can:</p>
                <ul style="text-align: left; display: inline-block;">
                    <li>🔍 Analyze your music preferences</li>
                    <li>📈 Track your listening patterns</li>
                    <li>🎯 Discover music insights</li>
                    <li>📊 Export your data for analysis</li>
                </ul>
                
                <br>
                <a href="/db-stats" class="btn">📊 View Database Stats</a>
                <a href="/" class="btn">🔄 Collect Again</a>
            </div>
            
            <p><strong>Note:</strong> Data collection now uses the comprehensive SpotifyDataCollector system with database storage.</p>
        </body>
        </html>
        '''
        
    except Exception as e:
        print(f"❌ Error during data collection: {e}")
        import traceback
        traceback.print_exc()
        
        return f'''
        <html>
        <head><title>❌ Error - Spotify MusiVault</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #191414; color: white;">
            <h1>❌ Collection Error</h1>
            <p>There was an error collecting your data:</p>
            <pre style="background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; text-align: left; display: inline-block;">{str(e)}</pre>
            <br>
            <a href="/" style="background: #1DB954; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px;">🔄 Try Again</a>
        </body>
        </html>
        '''

@app.route('/db-stats')
def database_stats():
    """Get database statistics."""
    try:
        stats = SpotifyDataStorage.get_database_stats()
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
    print("🎵 Starting Spotify MusiVault server...")
    print("🌐 Visit: http://127.0.0.1:5000")
    print("📝 Press Ctrl+C to stop")
    app.run(debug=True, host='127.0.0.1', port=5000)
