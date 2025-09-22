import os
import spotipy
from dotenv import load_dotenv
from authlib.integrations.flask_client import OAuth
from flask import Flask, redirect, request, url_for
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
    sp = spotipy.Spotify(auth=token_info['access_token'])

    # Use the new comprehensive data collection system
    collector = SpotifyDataCollector(sp)
    collection_result = collector.collect_all_user_data()
    
    if collection_result['success']:
        profile = sp.current_user()
        return f'''
        <h1>Data Collection Complete!</h1>
        <p>Successfully collected and stored Spotify data for: <strong>{profile['id']}</strong></p>
        <h3>Collection Summary:</h3>
        <ul>
            <li>Users: {collection_result['database_stats']['users']}</li>
            <li>Artists: {collection_result['database_stats']['artists']}</li>
            <li>Albums: {collection_result['database_stats']['albums']}</li>
            <li>Tracks: {collection_result['database_stats']['tracks']}</li>
            <li>Playlists: {collection_result['database_stats']['playlists']}</li>
            <li>Saved Tracks: {collection_result['database_stats']['saved_tracks']}</li>
            <li>Audio Features: {collection_result['database_stats']['audio_features']}</li>
        </ul>
        <p>Collection time: {collection_result['elapsed_time']:.2f} seconds</p>
        <p>Errors encountered: {collection_result['total_errors']}</p>
        <p><a href="/db-stats">View detailed database statistics</a></p>
        '''
    else:
        return f'''
        <h1>Data Collection Failed</h1>
        <p>Error: {collection_result.get('error', 'Unknown error')}</p>
        <p><a href="/login">Try again</a></p>
        '''

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

def fetch_and_print_spotify_data(sp):
    """
    Legacy function - now replaced by SpotifyDataCollector.
    Kept for reference but no longer used in the main flow.
    """
    # This function has been replaced by the comprehensive SpotifyDataCollector
    print("ℹ️  This function has been replaced by SpotifyDataCollector")
    print("   All data collection now uses the database storage system")

@app.route('/collect-data')
def collect_data_manually():
    """Manual data collection endpoint for testing."""
    try:
        # This would require a valid token - for now just return info
        return '''
        <h1>Manual Data Collection</h1>
        <p>To collect data manually, use the main authorization flow:</p>
        <ol>
            <li><a href="/login">Login with Spotify</a></li>
            <li>The authorization process will automatically collect and store your data</li>
            <li><a href="/db-stats">View collected data statistics</a></li>
        </ol>
        <p><strong>Note:</strong> Data collection now uses the comprehensive SpotifyDataCollector system with database storage.</p>
        '''
    except Exception as e:
        return f'Error: {str(e)}', 500

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
    app.run(debug=True)
