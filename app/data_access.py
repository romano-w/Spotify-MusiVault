"""
Data Access Layer (DAL) for Spotify MusiVault.
Provides high-level database operations for Spotify data storage and retrieval.
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Union
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import (
    User, Artist, Album, Track, Playlist, AudioFeatures, AudioAnalysis,
    SavedTrack, UserTopTrack, UserTopArtist,
    playlist_track_association, track_artist_association, album_artist_association,
    user_followed_artists_association
)
from app.database import db_session

class SpotifyDataStorage:
    """Enhanced data storage operations for Spotify entities with batch processing."""
    
    @staticmethod
    def store_user_data(user_data: dict) -> dict:
        """Store or update user data and return stored user info."""
        with db_session() as session:
            user = session.query(User).filter(User.id == user_data['id']).first()
            
            user_info = {
                'id': user_data['id'],
                'display_name': user_data.get('display_name'),
                'email': user_data.get('email'),
                'country': user_data.get('country'),
                'followers_total': user_data.get('followers', {}).get('total', 0),
                'spotify_url': user_data.get('external_urls', {}).get('spotify'),
                'href': user_data.get('href'),
                'uri': user_data.get('uri'),
                'product': user_data.get('product')
            }
            
            if user:
                # Update existing user
                for key, value in user_info.items():
                    if key != 'id':
                        setattr(user, key, value)
                user.updated_at = datetime.utcnow()
                print(f"📝 Updated existing user: {user.display_name or user.id}")
            else:
                # Create new user
                user = User(**user_info)
                session.add(user)
                print(f"✨ Created new user: {user.display_name or user.id}")
            
            session.commit()
            return user_info
    
    @staticmethod
    def store_artist_data(artist_data: dict) -> dict:
        """Store or update artist data."""
        with db_session() as session:
            artist = session.query(Artist).filter(Artist.id == artist_data['id']).first()
            
            artist_info = {
                'id': artist_data['id'],
                'name': artist_data['name'],
                'genres': json.dumps(artist_data.get('genres', [])),
                'popularity': artist_data.get('popularity'),
                'followers_total': artist_data.get('followers', {}).get('total', 0),
                'spotify_url': artist_data.get('external_urls', {}).get('spotify'),
                'href': artist_data.get('href'),
                'uri': artist_data.get('uri'),
                'images': json.dumps(artist_data.get('images', []))
            }
            
            if artist:
                # Update existing artist
                for key, value in artist_info.items():
                    if key != 'id':
                        setattr(artist, key, value)
                artist.updated_at = datetime.utcnow()
            else:
                # Create new artist
                artist = Artist(**artist_info)
                session.add(artist)
            
            session.commit()
            return artist_info
    
    @staticmethod
    def store_album_data(album_data: dict) -> dict:
        """Store or update album data."""
        with db_session() as session:
            album = session.query(Album).filter(Album.id == album_data['id']).first()
            
            album_info = {
                'id': album_data['id'],
                'name': album_data['name'],
                'album_type': album_data.get('album_type'),
                'total_tracks': album_data.get('total_tracks'),
                'release_date': album_data.get('release_date'),
                'release_date_precision': album_data.get('release_date_precision'),
                'available_markets': json.dumps(album_data.get('available_markets', [])),
                'spotify_url': album_data.get('external_urls', {}).get('spotify'),
                'href': album_data.get('href'),
                'uri': album_data.get('uri'),
                'images': json.dumps(album_data.get('images', [])),
                'label': album_data.get('label'),
                'popularity': album_data.get('popularity')
            }
            
            if album:
                # Update existing album
                for key, value in album_info.items():
                    if key != 'id':
                        setattr(album, key, value)
                album.updated_at = datetime.utcnow()
            else:
                # Create new album
                album = Album(**album_info)
                session.add(album)
            
            session.commit()
            return album_info
    
    @staticmethod
    def store_track_data(track_data: dict, album_id: Optional[str] = None) -> dict:
        """Store or update track data."""
        with db_session() as session:
            track = session.query(Track).filter(Track.id == track_data['id']).first()
            
            track_info = {
                'id': track_data['id'],
                'name': track_data['name'],
                'duration_ms': track_data.get('duration_ms'),
                'explicit': track_data.get('explicit', False),
                'popularity': track_data.get('popularity'),
                'preview_url': track_data.get('preview_url'),
                'track_number': track_data.get('track_number'),
                'disc_number': track_data.get('disc_number', 1),
                'is_local': track_data.get('is_local', False),
                'available_markets': json.dumps(track_data.get('available_markets', [])),
                'spotify_url': track_data.get('external_urls', {}).get('spotify'),
                'href': track_data.get('href'),
                'uri': track_data.get('uri'),
                'external_ids': json.dumps(track_data.get('external_ids', {})),
                'album_id': album_id or track_data.get('album', {}).get('id')
            }
            
            if track:
                # Update existing track
                for key, value in track_info.items():
                    if key != 'id':
                        setattr(track, key, value)
                track.updated_at = datetime.utcnow()
            else:
                # Create new track
                track = Track(**track_info)
                session.add(track)
            
            session.commit()
            return track_info
    
    @staticmethod
    def store_playlist_data(playlist_data: dict, owner_id: str) -> dict:
        """Store or update playlist data."""
        with db_session() as session:
            playlist = session.query(Playlist).filter(Playlist.id == playlist_data['id']).first()
            
            playlist_info = {
                'id': playlist_data['id'],
                'name': playlist_data['name'],
                'description': playlist_data.get('description'),
                'public': playlist_data.get('public'),
                'collaborative': playlist_data.get('collaborative', False),
                'followers_total': playlist_data.get('followers', {}).get('total', 0),
                'snapshot_id': playlist_data.get('snapshot_id'),
                'spotify_url': playlist_data.get('external_urls', {}).get('spotify'),
                'href': playlist_data.get('href'),
                'uri': playlist_data.get('uri'),
                'images': json.dumps(playlist_data.get('images', [])),
                'primary_color': playlist_data.get('primary_color'),
                'owner_id': owner_id
            }
            
            if playlist:
                # Update existing playlist
                for key, value in playlist_info.items():
                    if key != 'id':
                        setattr(playlist, key, value)
                playlist.updated_at = datetime.utcnow()
            else:
                # Create new playlist
                playlist = Playlist(**playlist_info)
                session.add(playlist)
            
            session.commit()
            return playlist_info
    
    @staticmethod
    def store_audio_features(features_data: dict) -> dict:
        """Store or update audio features for a track."""
        with db_session() as session:
            features = session.query(AudioFeatures).filter(
                AudioFeatures.track_id == features_data['id']
            ).first()
            
            features_info = {
                'track_id': features_data['id'],
                'danceability': features_data.get('danceability'),
                'energy': features_data.get('energy'),
                'key': features_data.get('key'),
                'loudness': features_data.get('loudness'),
                'mode': features_data.get('mode'),
                'speechiness': features_data.get('speechiness'),
                'acousticness': features_data.get('acousticness'),
                'instrumentalness': features_data.get('instrumentalness'),
                'liveness': features_data.get('liveness'),
                'valence': features_data.get('valence'),
                'tempo': features_data.get('tempo'),
                'time_signature': features_data.get('time_signature')
            }
            
            if features:
                # Update existing features
                for key, value in features_info.items():
                    if key != 'track_id':
                        setattr(features, key, value)
                features.updated_at = datetime.utcnow()
            else:
                # Create new features
                features = AudioFeatures(**features_info)
                session.add(features)
            
            session.commit()
            return features_info
    
    @staticmethod
    def store_audio_analysis(analysis_data: dict, track_id: str) -> dict:
        """Store or update audio analysis for a track."""
        with db_session() as session:
            analysis = session.query(AudioAnalysis).filter(
                AudioAnalysis.track_id == track_id
            ).first()
            
            analysis_info = {
                'track_id': track_id,
                'bars': json.dumps(analysis_data.get('bars', [])),
                'beats': json.dumps(analysis_data.get('beats', [])),
                'sections': json.dumps(analysis_data.get('sections', [])),
                'segments': json.dumps(analysis_data.get('segments', [])),
                'tatums': json.dumps(analysis_data.get('tatums', [])),
                'track_analysis': json.dumps(analysis_data.get('track', {}))
            }
            
            if analysis:
                # Update existing analysis
                for key, value in analysis_info.items():
                    if key != 'track_id':
                        setattr(analysis, key, value)
                analysis.updated_at = datetime.utcnow()
            else:
                # Create new analysis
                analysis = AudioAnalysis(**analysis_info)
                session.add(analysis)
            
            session.commit()
            return analysis_info
    
    @staticmethod
    def store_user_saved_tracks(user_id: str, saved_tracks_data: list) -> int:
        """Store user's saved tracks."""
        stored_count = 0
        with db_session() as session:
            for item in saved_tracks_data:
                track_data = item.get('track', {})
                added_at = item.get('added_at')
                
                # Check if already exists
                existing = session.query(SavedTrack).filter(
                    SavedTrack.user_id == user_id,
                    SavedTrack.track_id == track_data['id']
                ).first()
                
                if not existing:
                    saved_track = SavedTrack(
                        user_id=user_id,
                        track_id=track_data['id'],
                        added_at=datetime.fromisoformat(added_at.replace('Z', '+00:00')) if added_at else datetime.utcnow()
                    )
                    session.add(saved_track)
                    stored_count += 1
            
            session.commit()
        return stored_count
    
    @staticmethod
    def store_user_top_tracks(user_id: str, top_tracks_data: list, time_range: str = 'medium_term') -> int:
        """Store user's top tracks."""
        stored_count = 0
        with db_session() as session:
            # Remove existing top tracks for this time range
            session.query(UserTopTrack).filter(
                UserTopTrack.user_id == user_id,
                UserTopTrack.time_range == time_range
            ).delete()
            
            for rank, track_data in enumerate(top_tracks_data, 1):
                top_track = UserTopTrack(
                    user_id=user_id,
                    track_id=track_data['id'],
                    time_range=time_range,
                    rank=rank
                )
                session.add(top_track)
                stored_count += 1
            
            session.commit()
        return stored_count
    
    @staticmethod
    def store_user_top_artists(user_id: str, top_artists_data: list, time_range: str = 'medium_term') -> int:
        """Store user's top artists."""
        stored_count = 0
        with db_session() as session:
            # Remove existing top artists for this time range
            session.query(UserTopArtist).filter(
                UserTopArtist.user_id == user_id,
                UserTopArtist.time_range == time_range
            ).delete()
            
            for rank, artist_data in enumerate(top_artists_data, 1):
                top_artist = UserTopArtist(
                    user_id=user_id,
                    artist_id=artist_data['id'],
                    time_range=time_range,
                    rank=rank
                )
                session.add(top_artist)
                stored_count += 1
            
            session.commit()
        return stored_count
    
    @staticmethod
    def link_track_artists(track_id: str, artists_data: list):
        """Create associations between tracks and artists."""
        with db_session() as session:
            # Remove existing associations
            session.execute(
                track_artist_association.delete().where(
                    track_artist_association.c.track_id == track_id
                )
            )
            
            # Add new associations
            for artist_data in artists_data:
                session.execute(
                    track_artist_association.insert().values(
                        track_id=track_id,
                        artist_id=artist_data['id']
                    )
                )
            
            session.commit()
    
    @staticmethod
    def link_album_artists(album_id: str, artists_data: list):
        """Create associations between albums and artists."""
        with db_session() as session:
            # Remove existing associations
            session.execute(
                album_artist_association.delete().where(
                    album_artist_association.c.album_id == album_id
                )
            )
            
            # Add new associations
            for artist_data in artists_data:
                session.execute(
                    album_artist_association.insert().values(
                        album_id=album_id,
                        artist_id=artist_data['id']
                    )
                )
            
            session.commit()
    
    @staticmethod
    def link_playlist_tracks(playlist_id: str, tracks_data: list):
        """Create associations between playlists and tracks."""
        with db_session() as session:
            # Remove existing associations
            session.execute(
                playlist_track_association.delete().where(
                    playlist_track_association.c.playlist_id == playlist_id
                )
            )
            
            # Add new associations
            for position, item in enumerate(tracks_data):
                track_data = item.get('track', {})
                added_at = item.get('added_at')
                added_by = item.get('added_by', {}).get('id')
                
                session.execute(
                    playlist_track_association.insert().values(
                        playlist_id=playlist_id,
                        track_id=track_data['id'],
                        added_at=datetime.fromisoformat(added_at.replace('Z', '+00:00')) if added_at else None,
                        added_by_id=added_by,
                        position=position
                    )
                )
            
            session.commit()
    
    @staticmethod
    def get_database_stats() -> dict:
        """Get comprehensive database statistics."""
        with db_session() as session:
            stats = {
                'users': session.query(User).count(),
                'artists': session.query(Artist).count(),
                'albums': session.query(Album).count(),
                'tracks': session.query(Track).count(),
                'playlists': session.query(Playlist).count(),
                'audio_features': session.query(AudioFeatures).count(),
                'audio_analysis': session.query(AudioAnalysis).count(),
                'saved_tracks': session.query(SavedTrack).count(),
                'user_top_tracks': session.query(UserTopTrack).count(),
                'user_top_artists': session.query(UserTopArtist).count(),
            }
            return stats

# Legacy compatibility - keep the old class name
SpotifyDataAccess = SpotifyDataStorage
