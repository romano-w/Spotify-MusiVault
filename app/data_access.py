"""
Data Access Layer (DAL) for Spotify MusiVault.
Provides high-level database operations for Spotify data.
"""

import json
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from .models import (
    User, Artist, Album, Track, Playlist, AudioFeatures, AudioAnalysis,
    SavedTrack, UserTopTrack, UserTopArtist,
    playlist_track_association, track_artist_association, album_artist_association
)
from .database import db_session

class SpotifyDataAccess:
    """Data access operations for Spotify entities."""
    
    @staticmethod
    def create_or_update_user(user_data: dict) -> dict:
        """Create or update a user record."""
        with db_session() as session:
            user = session.query(User).filter(User.id == user_data['id']).first()
            
            if user:
                # Update existing user
                user.display_name = user_data.get('display_name')
                user.email = user_data.get('email')
                user.country = user_data.get('country')
                user.followers_total = user_data.get('followers', {}).get('total', 0)
                user.spotify_url = user_data.get('external_urls', {}).get('spotify')
                user.href = user_data.get('href')
                user.uri = user_data.get('uri')
                user.product = user_data.get('product')
                user.updated_at = datetime.utcnow()
            else:
                # Create new user
                user = User(
                    id=user_data['id'],
                    display_name=user_data.get('display_name'),
                    email=user_data.get('email'),
                    country=user_data.get('country'),
                    followers_total=user_data.get('followers', {}).get('total', 0),
                    spotify_url=user_data.get('external_urls', {}).get('spotify'),
                    href=user_data.get('href'),
                    uri=user_data.get('uri'),
                    product=user_data.get('product')
                )
                session.add(user)
            
            session.commit()
            # Return a dictionary with the user data instead of the object
            return {
                'id': user.id,
                'display_name': user.display_name,
                'email': user.email,
                'country': user.country,
                'followers_total': user.followers_total,
                'spotify_url': user.spotify_url,
                'href': user.href,
                'uri': user.uri,
                'product': user.product
            }
    
    @staticmethod
    def create_or_update_artist(artist_data: dict) -> dict:
        """Create or update an artist record."""
        with db_session() as session:
            artist = session.query(Artist).filter(Artist.id == artist_data['id']).first()
            
            artist_dict = {
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
                for key, value in artist_dict.items():
                    if key != 'id':
                        setattr(artist, key, value)
                artist.updated_at = datetime.utcnow()
            else:
                # Create new artist
                artist = Artist(**artist_dict)
                session.add(artist)
            
            session.commit()
            return {
                'id': artist.id,
                'name': artist.name,
                'genres': artist.genres,
                'popularity': artist.popularity,
                'followers_total': artist.followers_total,
                'spotify_url': artist.spotify_url,
                'href': artist.href,
                'uri': artist.uri,
                'images': artist.images
            }
    
    @staticmethod
    def create_or_update_album(album_data: dict) -> Album:
        """Create or update an album record."""
        with db_session() as session:
            album = session.query(Album).filter(Album.id == album_data['id']).first()
            
            album_dict = {
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
                for key, value in album_dict.items():
                    if key != 'id':
                        setattr(album, key, value)
                album.updated_at = datetime.utcnow()
            else:
                # Create new album
                album = Album(**album_dict)
                session.add(album)
            
            session.commit()
            return album
    
    @staticmethod
    def create_or_update_track(track_data: dict, album_id=None) -> dict:
        """Create or update a track record."""
        with db_session() as session:
            track = session.query(Track).filter(Track.id == track_data['id']).first()
            
            track_dict = {
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
                for key, value in track_dict.items():
                    if key != 'id':
                        setattr(track, key, value)
                track.updated_at = datetime.utcnow()
            else:
                # Create new track
                track = Track(**track_dict)
                session.add(track)
            
            session.commit()
            return {
                'id': track.id,
                'name': track.name,
                'duration_ms': track.duration_ms,
                'explicit': track.explicit,
                'popularity': track.popularity,
                'preview_url': track.preview_url,
                'track_number': track.track_number,
                'disc_number': track.disc_number,
                'is_local': track.is_local,
                'album_id': track.album_id
            }
    
    @staticmethod
    def create_or_update_playlist(playlist_data: dict, owner_id: str) -> Playlist:
        """Create or update a playlist record."""
        with db_session() as session:
            playlist = session.query(Playlist).filter(Playlist.id == playlist_data['id']).first()
            
            playlist_dict = {
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
                for key, value in playlist_dict.items():
                    if key != 'id':
                        setattr(playlist, key, value)
                playlist.updated_at = datetime.utcnow()
            else:
                # Create new playlist
                playlist = Playlist(**playlist_dict)
                session.add(playlist)
            
            session.commit()
            return playlist
    
    @staticmethod
    def create_or_update_audio_features(features_data: dict) -> AudioFeatures:
        """Create or update audio features for a track."""
        with db_session() as session:
            features = session.query(AudioFeatures).filter(
                AudioFeatures.track_id == features_data['id']
            ).first()
            
            features_dict = {
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
                for key, value in features_dict.items():
                    if key != 'track_id':
                        setattr(features, key, value)
                features.updated_at = datetime.utcnow()
            else:
                # Create new features
                features = AudioFeatures(**features_dict)
                session.add(features)
            
            session.commit()
            return features
    
    @staticmethod
    def save_user_saved_track(user_id: str, track_data: dict, added_at=None):
        """Save a user's saved track."""
        with db_session() as session:
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
                session.commit()
    
    @staticmethod
    def get_user(user_id: str) -> User:
        """Get a user by ID."""
        with db_session() as session:
            return session.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_playlists(user_id: str) -> list:
        """Get all playlists for a user."""
        with db_session() as session:
            return session.query(Playlist).filter(Playlist.owner_id == user_id).all()
    
    @staticmethod
    def get_database_stats() -> dict:
        """Get database statistics."""
        with db_session() as session:
            stats = {
                'users': session.query(User).count(),
                'artists': session.query(Artist).count(),
                'albums': session.query(Album).count(),
                'tracks': session.query(Track).count(),
                'playlists': session.query(Playlist).count(),
                'audio_features': session.query(AudioFeatures).count(),
                'saved_tracks': session.query(SavedTrack).count()
            }
            return stats
