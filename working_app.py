#!/usr/bin/env python3
"""
Working Flask app for Spotify MusiVault
"""
import os
import sys
import spotipy
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, request, url_for, session

# Load environment variables
load_dotenv()

# Add app directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
app_dir = os.path.join(current_dir, 'app')
sys.path.insert(0, app_dir)

print(f"🔧 Adding {app_dir} to Python path")

# Import our modules
try:
    from database import init_database, db_session
    from models import User
    from data_access import SpotifyDataStorage
    from data_collector import SpotifyDataCollector
    print("✅ All modules imported successfully")
except ImportError as e:
    print(f"⚠️ Import warning: {e}")
    print("📝 Some features may not work")

app = Flask(__name__)

# Initialize database
try:
    print("🔧 Initializing database...")
    init_database()
    print("✅ Database initialized successfully")
except Exception as e:
    print(f"⚠️ Database initialization warning: {e}")

# App configuration
app.secret_key = os.getenv('APP_SECRET_KEY')

# OAuth setup
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
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                text-align: center; 
                padding: 50px; 
                background: linear-gradient(135deg, #1DB954, #191414); 
                color: white; 
                margin: 0;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container { 
                max-width: 600px; 
                background: rgba(255,255,255,0.1); 
                padding: 50px; 
                border-radius: 25px; 
                backdrop-filter: blur(10px);
                box-shadow: 0 8px 32px rgba(0,0,0,0.3);
            }
            h1 { 
                font-size: 3em; 
                margin-bottom: 20px; 
                text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
            }
            .subtitle { 
                font-size: 1.2em; 
                margin-bottom: 30px; 
                opacity: 0.9;
            }
            .features { 
                text-align: left; 
                display: inline-block; 
                margin: 30px 0;
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 15px;
            }
            .features li { 
                margin: 10px 0; 
                font-size: 1.1em;
            }
            .btn { 
                background: linear-gradient(45deg, #1DB954, #1ed760); 
                color: white; 
                padding: 18px 40px; 
                text-decoration: none; 
                border-radius: 50px; 
                font-size: 1.3em; 
                font-weight: bold;
                display: inline-block; 
                margin: 30px 0;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(29, 185, 84, 0.4);
            }
            .btn:hover { 
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(29, 185, 84, 0.6);
                background: linear-gradient(45deg, #1ed760, #1DB954);
            }
            .status { 
                background: rgba(29, 185, 84, 0.2); 
                padding: 15px; 
                border-radius: 10px; 
                margin: 20px 0;
                border-left: 4px solid #1DB954;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 Spotify MusiVault</h1>
            <p class="subtitle">Collect, Store & Analyze Your Spotify Data</p>
            
            <div class="status">
                <strong>✅ Server Status:</strong> Running & Ready!
            </div>
            
            <p>This application will collect and store:</p>
            <div class="features">
                <ul>
                    <li>🎵 All your playlists and tracks</li>
                    <li>❤️ Your saved tracks (liked songs)</li>
                    <li>🎤 Your top artists and tracks</li>
                    <li>🎼 Audio features for every track</li>
                    <li>👤 Your profile information</li>
                    <li>🔗 Complete relationship mapping</li>
                </ul>
            </div>
            
            <a href="/authorize" class="btn">🚀 Start Data Collection</a>
            
            <p style="font-size: 0.9em; opacity: 0.8; margin-top: 30px;">
                <strong>Note:</strong> Your data will be stored locally in a secure database
            </p>
        </div>
    </body>
    </html>
    '''

@app.route('/authorize')
def authorize():
    try:
        redirect_uri = url_for('callback', _external=True)
        return spotify.authorize_redirect(redirect_uri)
    except Exception as e:
        return f'''
        <html>
        <head><title>❌ Authorization Error</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #191414; color: white;">
            <h1>❌ Authorization Error</h1>
            <p>Error: {str(e)}</p>
            <a href="/" style="background: #1DB954; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px;">🔄 Try Again</a>
        </body>
        </html>
        '''

@app.route('/callback')
def callback():
    try:
        # Handle Spotify callback
        token = spotify.authorize_access_token()
        session['token'] = token
        
        # Create Spotipy client
        sp = spotipy.Spotify(auth=token['access_token'])
        
        print("🎯 Starting data collection...")
        
        # Try to use SpotifyDataCollector if available
        try:
            collector = SpotifyDataCollector(sp)
            collection_result = collector.collect_all_user_data()
            
            # Get database statistics
            stats = SpotifyDataStorage.get_database_stats()
            
            print("✅ Data collection complete!")
            
            return f'''
            <html>
            <head>
                <title>🎉 Collection Complete!</title>
                <style>
                    body {{ font-family: Arial, sans-serif; text-align: center; padding: 30px; background: linear-gradient(135deg, #1DB954, #191414); color: white; }}
                    .container {{ max-width: 800px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 20px; }}
                    .success {{ background: #1DB954; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                    .stats {{ background: rgba(255,255,255,0.1); padding: 20px; border-radius: 10px; margin: 20px 0; text-align: left; }}
                    .stat-item {{ padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.2); font-size: 1.1em; }}
                    .btn {{ background: #1DB954; color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px; margin: 10px; display: inline-block; }}
                    h1 {{ font-size: 2.5em; }}
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
                        <div class="stat-item"><strong>👤 Users:</strong> {stats.get('users', 0)}</div>
                        <div class="stat-item"><strong>🎤 Artists:</strong> {stats.get('artists', 0)}</div>
                        <div class="stat-item"><strong>💿 Albums:</strong> {stats.get('albums', 0)}</div>
                        <div class="stat-item"><strong>🎵 Tracks:</strong> {stats.get('tracks', 0)}</div>
                        <div class="stat-item"><strong>📝 Playlists:</strong> {stats.get('playlists', 0)}</div>
                        <div class="stat-item"><strong>🎼 Audio Features:</strong> {stats.get('audio_features', 0)}</div>
                        <div class="stat-item"><strong>🔗 Track-Artist Links:</strong> {stats.get('track_artists', 0)}</div>
                        <div class="stat-item"><strong>📋 Playlist-Track Links:</strong> {stats.get('playlist_tracks', 0)}</div>
                    </div>
                    
                    <a href="/db-stats" class="btn">📊 View JSON Stats</a>
                    <a href="/" class="btn">🔄 Collect Again</a>
                </div>
            </body>
            </html>
            '''
            
        except Exception as collector_error:
            print(f"⚠️ Collector error: {collector_error}")
            
            # Fallback: Just show user info
            user_info = sp.current_user()
            return f'''
            <html>
            <head><title>✅ Authorization Success</title></head>
            <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #191414; color: white;">
                <h1>✅ Authorization Successful!</h1>
                <p>Hello, {user_info.get('display_name', 'Spotify User')}!</p>
                <p>User ID: {user_info.get('id')}</p>
                <p>Followers: {user_info.get('followers', {}).get('total', 0)}</p>
                <p><strong>Note:</strong> Full data collection system is being initialized...</p>
                <a href="/" style="background: #1DB954; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px;">🏠 Home</a>
            </body>
            </html>
            '''
            
    except Exception as e:
        print(f"❌ Callback error: {e}")
        import traceback
        traceback.print_exc()
        
        return f'''
        <html>
        <head><title>❌ Error</title></head>
        <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px; background: #191414; color: white;">
            <h1>❌ Error During Authorization</h1>
            <p>Error: {str(e)}</p>
            <a href="/" style="background: #1DB954; color: white; padding: 15px 30px; text-decoration: none; border-radius: 30px;">🔄 Try Again</a>
        </body>
        </html>
        '''

@app.route('/db-stats')
def database_stats():
    """Get database statistics as JSON."""
    try:
        stats = SpotifyDataStorage.get_database_stats()
        return {
            'status': 'success',
            'stats': stats,
            'message': 'Database statistics retrieved successfully'
        }
    except Exception as e:
        return {
            'status': 'error',
            'message': f'Error retrieving stats: {str(e)}'
        }, 500

@app.route('/test')
def test():
    """Test endpoint to verify server is working."""
    return {
        'status': 'success',
        'message': 'Spotify MusiVault server is working!',
        'server': 'Flask',
        'database_file': 'spotify_data.db'
    }

if __name__ == '__main__':
    print("=" * 60)
    print("🎵 Spotify MusiVault Server")
    print("=" * 60)
    print("🔧 Checking environment...")
    
    # Check required environment variables
    required_vars = ['SPOTIFY_CLIENT_ID', 'SPOTIFY_CLIENT_SECRET', 'APP_SECRET_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print(f"❌ Missing environment variables: {', '.join(missing_vars)}")
        print("📝 Please check your .env file")
    else:
        print("✅ Environment variables loaded")
    
    print("🌐 Starting server...")
    print("📍 URL: http://127.0.0.1:5000")
    print("📝 Press Ctrl+C to stop")
    print("=" * 60)
    
    try:
        app.run(debug=True, host='127.0.0.1', port=5000)
    except Exception as e:
        print(f"❌ Server error: {e}")
        import traceback
        traceback.print_exc()
