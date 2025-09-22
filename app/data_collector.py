"""
Spotify Data Collection Orchestrator - Phase 2+ Implementation
Systematically collects and stores all Spotify data with proper error handling and progress tracking.
"""

import time
from typing import Dict, List, Optional
from datetime import datetime
from data_access import SpotifyDataStorage
from spotify_api_services import (
    get_user, get_user_playlists, get_playlist, get_playlist_items,
    get_saved_tracks, get_user_top_items, get_followed_artists,
    get_several_audio_features, get_track_audio_features, get_track_audio_analysis
)
from retry_utils import retry_request
from database import db_session
from models import Track, AudioFeatures
import os

class SpotifyDataCollector:
    """
    Orchestrates the complete collection and storage of Spotify user data.
    Replaces console printing with systematic database storage.
    """
    
    def __init__(self, spotify_client):
        self.sp = spotify_client
        self.storage = SpotifyDataStorage()
        self.stats = {
            'users': 0,
            'artists': 0,
            'albums': 0,
            'tracks': 0,
            'playlists': 0,
            'audio_features': 0,
            'audio_analysis': 0,
            'saved_tracks': 0,
            'playlist_tracks': 0,
            'errors': 0
        }
        
    def collect_all_user_data(self) -> Dict:
        """
        Main orchestrator method - collects and stores all Spotify data for the authenticated user.
        """
        print("🚀 Starting comprehensive Spotify data collection...")
        print("=" * 70)
        
        start_time = time.time()
        
        try:
            # Step 1: Collect and store user profile
            user_data = self._collect_user_profile()
            if not user_data:
                print("❌ Failed to get user profile. Aborting collection.")
                return {'success': False, 'error': 'No user profile'}
            
            user_id = user_data['id']
            print(f"👤 Collecting data for user: {user_data.get('display_name', user_id)}")
            print("-" * 70)
            
            # Step 2: Collect and store playlists (with tracks)
            self._collect_user_playlists(user_id)
            
            # Step 3: Collect and store saved tracks
            self._collect_saved_tracks(user_id)
            
            # Step 4: Collect and store top tracks and artists
            self._collect_top_items(user_id)
            
            # Step 5: Collect and store followed artists
            self._collect_followed_artists(user_id)
            
            # Step 6: Enhance tracks with audio features
            self._collect_audio_features()

            # Step 6b: Optional audio analysis (heavier)
            enable_analysis = os.getenv('ENABLE_AUDIO_ANALYSIS', 'false').lower() in ('1', 'true', 'yes')
            if enable_analysis:
                self._collect_audio_analysis()
            
            # Step 7: Generate final report
            elapsed_time = time.time() - start_time
            return self._generate_collection_report(elapsed_time)
            
        except Exception as e:
            print(f"❌ Critical error during data collection: {e}")
            self.stats['errors'] += 1
            return {
                'success': False, 
                'error': str(e),
                'stats': self.stats
            }
    
    def _collect_user_profile(self) -> Optional[Dict]:
        """Collect and store user profile data."""
        try:
            print("📋 Collecting user profile...")
            user_data = get_user(self.sp)
            
            if user_data:
                stored_user = self.storage.store_user_data(user_data)
                self.stats['users'] += 1
                print(f"✅ User profile stored: {stored_user.get('display_name', stored_user['id'])}")
                return stored_user
            else:
                print("❌ No user data received")
                return None
                
        except Exception as e:
            print(f"❌ Error collecting user profile: {e}")
            self.stats['errors'] += 1
            return None
    
    def _collect_user_playlists(self, user_id: str):
        """Collect and store all user playlists with their tracks."""
        try:
            print("🎵 Collecting user playlists...")
            playlists = get_user_playlists(self.sp)
            
            if not playlists:
                print("ℹ️  No playlists found")
                return
                
            print(f"📂 Found {len(playlists)} playlists")
            
            for i, playlist_data in enumerate(playlists, 1):
                try:
                    print(f"  📋 Processing playlist {i}/{len(playlists)}: {playlist_data['name']}")
                    
                    # Store playlist
                    self.storage.store_playlist_data(playlist_data, user_id)
                    self.stats['playlists'] += 1
                    
                    # Get and store playlist tracks
                    playlist_tracks = get_playlist_items(self.sp, playlist_data['id'])
                    
                    if playlist_tracks:
                        track_count = self._process_playlist_tracks(playlist_data['id'], playlist_tracks)
                        print(f"    ✅ Stored {track_count} tracks")
                        self.stats['playlist_tracks'] += track_count
                    
                    # Small delay to respect rate limits
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"    ❌ Error processing playlist {playlist_data['name']}: {e}")
                    self.stats['errors'] += 1
                    continue
                    
        except Exception as e:
            print(f"❌ Error collecting playlists: {e}")
            self.stats['errors'] += 1
    
    def _process_playlist_tracks(self, playlist_id: str, tracks_data: List) -> int:
        """Process and store tracks from a playlist."""
        stored_count = 0
        
        for item in tracks_data:
            try:
                track_data = item.get('track')
                if not track_data or track_data.get('id') is None:
                    continue  # Skip invalid tracks
                
                # Store track
                self._store_track_with_dependencies(track_data)
                stored_count += 1
                
            except Exception as e:
                print(f"      ⚠️  Error processing track: {e}")
                self.stats['errors'] += 1
                continue
        
        # Link playlist to tracks
        try:
            self.storage.link_playlist_tracks(playlist_id, tracks_data)
        except Exception as e:
            print(f"      ⚠️  Error linking playlist tracks: {e}")
            self.stats['errors'] += 1
        
        return stored_count
    
    def _store_track_with_dependencies(self, track_data: Dict):
        """Store a track and all its dependencies (album, artists)."""
        # Store album if present
        album_data = track_data.get('album')
        if album_data:
            self.storage.store_album_data(album_data)
            self.stats['albums'] += 1
            
            # Store album artists
            album_artists = album_data.get('artists', [])
            for artist_data in album_artists:
                self.storage.store_artist_data(artist_data)
                self.stats['artists'] += 1
            
            # Link album to artists
            if album_artists:
                self.storage.link_album_artists(album_data['id'], album_artists)
        
        # Store track artists
        track_artists = track_data.get('artists', [])
        for artist_data in track_artists:
            self.storage.store_artist_data(artist_data)
            self.stats['artists'] += 1
        
        # Store the track
        album_id = album_data['id'] if album_data else None
        self.storage.store_track_data(track_data, album_id)
        self.stats['tracks'] += 1
        
        # Link track to artists
        if track_artists:
            self.storage.link_track_artists(track_data['id'], track_artists)
    
    def _collect_saved_tracks(self, user_id: str):
        """Collect and store user's saved tracks."""
        try:
            print("💾 Collecting saved tracks...")
            saved_tracks_data = get_saved_tracks(self.sp)
            
            if not saved_tracks_data:
                print("ℹ️  No saved tracks found")
                return
            
            print(f"💿 Found {len(saved_tracks_data)} saved tracks")
            
            # Process and store each saved track
            for item in saved_tracks_data:
                track_data = item.get('track')
                if track_data and track_data.get('id'):
                    self._store_track_with_dependencies(track_data)
            
            # Store saved tracks relationships
            saved_count = self.storage.store_user_saved_tracks(user_id, saved_tracks_data)
            self.stats['saved_tracks'] += saved_count
            
            print(f"✅ Stored {saved_count} saved tracks")
            
        except Exception as e:
            print(f"❌ Error collecting saved tracks: {e}")
            self.stats['errors'] += 1
    
    def _collect_top_items(self, user_id: str):
        """Collect and store user's top tracks and artists."""
        try:
            print("🏆 Collecting top tracks and artists...")
            
            ranges = ['short_term', 'medium_term', 'long_term']
            for r in ranges:
                # Top tracks for range
                top_tracks = get_user_top_items(self.sp, 'tracks', time_range=r)
                if top_tracks and 'items' in top_tracks:
                    tracks_data = top_tracks['items']
                    print(f"🎵 [{r}] Found {len(tracks_data)} top tracks")
                    # Store track dependencies
                    for track_data in tracks_data:
                        self._store_track_with_dependencies(track_data)
                    # Store top tracks relationships with time_range
                    top_tracks_count = self.storage.store_user_top_tracks(user_id, tracks_data, time_range=r)
                    print(f"✅ [{r}] Stored {top_tracks_count} top tracks")

                # Top artists for range
                top_artists = get_user_top_items(self.sp, 'artists', time_range=r)
                if top_artists and 'items' in top_artists:
                    artists_data = top_artists['items']
                    print(f"🎤 [{r}] Found {len(artists_data)} top artists")
                    for artist_data in artists_data:
                        self.storage.store_artist_data(artist_data)
                        self.stats['artists'] += 1
                    top_artists_count = self.storage.store_user_top_artists(user_id, artists_data, time_range=r)
                    print(f"✅ [{r}] Stored {top_artists_count} top artists")
                
        except Exception as e:
            print(f"❌ Error collecting top items: {e}")
            self.stats['errors'] += 1
    
    def _collect_followed_artists(self, user_id: str):
        """Collect and store user's followed artists."""
        try:
            print("👥 Collecting followed artists...")
            followed_artists = get_followed_artists(self.sp)
            
            if followed_artists:
                print(f"🎤 Found {len(followed_artists)} followed artists")
                
                # Store each followed artist
                for artist_data in followed_artists:
                    self.storage.store_artist_data(artist_data)
                    self.stats['artists'] += 1
                
                print(f"✅ Stored {len(followed_artists)} followed artists")
            else:
                print("ℹ️  No followed artists found")
                
        except Exception as e:
            print(f"❌ Error collecting followed artists: {e}")
            self.stats['errors'] += 1
    
    def _collect_audio_features(self):
        """Collect audio features for tracks missing them in batches of 100."""
        try:
            print("🎶 Collecting audio features for tracks...")

            # Gather track IDs that do not yet have audio features
            with db_session() as session:
                subq = session.query(AudioFeatures.track_id)
                track_ids = [tid for (tid,) in session.query(Track.id).filter(~Track.id.in_(subq)).all()]

            if not track_ids:
                print("ℹ️  No missing audio features; skipping")
                return

            print(f"📊 Missing audio features for {len(track_ids)} tracks; fetching in batches...")

            # Prepare retriable API call
            retriable_audio_features = retry_request(get_several_audio_features)

            BATCH_SIZE = 100
            total_added = 0
            for i in range(0, len(track_ids), BATCH_SIZE):
                batch = track_ids[i:i + BATCH_SIZE]
                try:
                    features_list = retriable_audio_features(self.sp, batch)
                    if not features_list:
                        continue
                    for feat in features_list:
                        if not feat or not feat.get('id'):
                            continue
                        self.storage.store_audio_features(feat)
                        total_added += 1
                except Exception as e:
                    print(f"⚠️  Batch {i//BATCH_SIZE + 1}: error fetching audio features: {e}")
                    self.stats['errors'] += 1
                    continue

                # Gentle pacing
                time.sleep(0.1)

            self.stats['audio_features'] += total_added
            print(f"✅ Stored audio features for {total_added} tracks")

        except Exception as e:
            print(f"❌ Error in audio features collection: {e}")
            self.stats['errors'] += 1

    def _collect_audio_analysis(self):
        """Collect audio analysis for tracks missing them, sequentially with pacing.

        Controlled by environment variables:
        - ENABLE_AUDIO_ANALYSIS: 'true' to enable (default 'false')
        - AUDIO_ANALYSIS_LIMIT: max tracks to analyze this run (default 100)
        - AUDIO_ANALYSIS_SLEEP: seconds between calls (default 0.2)
        """
        try:
            print("🧠 Collecting audio analysis for tracks...")
            limit = int(os.getenv('AUDIO_ANALYSIS_LIMIT', '100'))
            sleep_s = float(os.getenv('AUDIO_ANALYSIS_SLEEP', '0.2'))

            # Track IDs missing analysis
            with db_session() as session:
                existing_ids = set(r[0] for r in session.query(Track.id).join(
                    Track.audio_analysis, isouter=True
                ).filter(Track.audio_analysis == None).limit(limit).all())  # noqa: E711

            track_ids = list(existing_ids)
            if not track_ids:
                print("ℹ️  No missing audio analysis; skipping")
                return

            print(f"📊 Will fetch analysis for up to {len(track_ids)} tracks (limit={limit})...")

            retriable_analysis = retry_request(get_track_audio_analysis)
            added = 0
            for idx, tid in enumerate(track_ids, 1):
                try:
                    analysis = retriable_analysis(self.sp, tid)
                    if analysis:
                        self.storage.store_audio_analysis(analysis, tid)
                        added += 1
                except Exception as e:
                    print(f"⚠️  Error fetching analysis for {tid}: {e}")
                    self.stats['errors'] += 1
                time.sleep(sleep_s)

            self.stats['audio_analysis'] += added
            print(f"✅ Stored audio analysis for {added} tracks")

        except Exception as e:
            print(f"❌ Error in audio analysis collection: {e}")
            self.stats['errors'] += 1
    
    def _generate_collection_report(self, elapsed_time: float) -> Dict:
        """Generate a comprehensive collection report."""
        print("\n" + "=" * 70)
        print("📊 DATA COLLECTION COMPLETE!")
        print("=" * 70)
        
        # Get final database statistics
        final_stats = self.storage.get_database_stats()
        
        print("📈 COLLECTION SUMMARY:")
        print(f"  👤 Users: {final_stats['users']}")
        print(f"  🎤 Artists: {final_stats['artists']}")
        print(f"  💿 Albums: {final_stats['albums']}")
        print(f"  🎵 Tracks: {final_stats['tracks']}")
        print(f"  📋 Playlists: {final_stats['playlists']}")
        print(f"  💾 Saved Tracks: {final_stats['saved_tracks']}")
        print(f"  🏆 Top Items: {final_stats['user_top_tracks'] + final_stats['user_top_artists']}")
        print(f"  🎶 Audio Features: {final_stats['audio_features']}")
        print(f"  ❌ Errors: {self.stats['errors']}")
        
        print(f"\n⏱️  Total collection time: {elapsed_time:.2f} seconds")
        print("=" * 70)
        
        return {
            'success': True,
            'elapsed_time': elapsed_time,
            'database_stats': final_stats,
            'collection_stats': self.stats,
            'total_errors': self.stats['errors']
        }
