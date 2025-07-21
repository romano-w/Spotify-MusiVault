"""
Database models for Spotify MusiVault.
Defines SQLAlchemy models for storing Spotify data.
"""

from sqlalchemy import create_engine, Column, String, Integer, Boolean, Text, DateTime, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import os

Base = declarative_base()

# Association tables for many-to-many relationships
playlist_track_association = Table(
    'playlist_tracks',
    Base.metadata,
    Column('playlist_id', String, ForeignKey('playlists.id'), primary_key=True),
    Column('track_id', String, ForeignKey('tracks.id'), primary_key=True),
    Column('added_at', DateTime),
    Column('added_by_id', String),
    Column('position', Integer)
)

track_artist_association = Table(
    'track_artists',
    Base.metadata,
    Column('track_id', String, ForeignKey('tracks.id'), primary_key=True),
    Column('artist_id', String, ForeignKey('artists.id'), primary_key=True)
)

album_artist_association = Table(
    'album_artists',
    Base.metadata,
    Column('album_id', String, ForeignKey('albums.id'), primary_key=True),
    Column('artist_id', String, ForeignKey('artists.id'), primary_key=True)
)

user_followed_artists_association = Table(
    'user_followed_artists',
    Base.metadata,
    Column('user_id', String, ForeignKey('users.id'), primary_key=True),
    Column('artist_id', String, ForeignKey('artists.id'), primary_key=True),
    Column('followed_at', DateTime, default=datetime.utcnow)
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(String, primary_key=True)
    display_name = Column(String)
    email = Column(String)
    country = Column(String)
    followers_total = Column(Integer)
    spotify_url = Column(String)
    href = Column(String)
    uri = Column(String)
    product = Column(String)  # free, premium, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    playlists = relationship("Playlist", back_populates="owner")
    saved_tracks = relationship("SavedTrack", back_populates="user")
    top_tracks = relationship("UserTopTrack", back_populates="user")
    top_artists = relationship("UserTopArtist", back_populates="user")
    followed_artists = relationship("Artist", secondary=user_followed_artists_association, back_populates="followers")

class Artist(Base):
    __tablename__ = 'artists'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    genres = Column(Text)  # JSON string of genres list
    popularity = Column(Integer)
    followers_total = Column(Integer)
    spotify_url = Column(String)
    href = Column(String)
    uri = Column(String)
    images = Column(Text)  # JSON string of images list
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tracks = relationship("Track", secondary=track_artist_association, back_populates="artists")
    albums = relationship("Album", secondary=album_artist_association, back_populates="artists")
    followers = relationship("User", secondary=user_followed_artists_association, back_populates="followed_artists")
    top_for_users = relationship("UserTopArtist", back_populates="artist")

class Album(Base):
    __tablename__ = 'albums'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    album_type = Column(String)  # album, single, compilation
    total_tracks = Column(Integer)
    release_date = Column(String)
    release_date_precision = Column(String)  # year, month, day
    available_markets = Column(Text)  # JSON string
    spotify_url = Column(String)
    href = Column(String)
    uri = Column(String)
    images = Column(Text)  # JSON string of images list
    label = Column(String)
    popularity = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tracks = relationship("Track", back_populates="album")
    artists = relationship("Artist", secondary=album_artist_association, back_populates="albums")

class Track(Base):
    __tablename__ = 'tracks'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    duration_ms = Column(Integer)
    explicit = Column(Boolean)
    popularity = Column(Integer)
    preview_url = Column(String)
    track_number = Column(Integer)
    disc_number = Column(Integer)
    is_local = Column(Boolean)
    available_markets = Column(Text)  # JSON string
    spotify_url = Column(String)
    href = Column(String)
    uri = Column(String)
    external_ids = Column(Text)  # JSON string (ISRC, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    album_id = Column(String, ForeignKey('albums.id'))
    
    # Relationships
    album = relationship("Album", back_populates="tracks")
    artists = relationship("Artist", secondary=track_artist_association, back_populates="tracks")
    playlists = relationship("Playlist", secondary=playlist_track_association, back_populates="tracks")
    audio_features = relationship("AudioFeatures", back_populates="track", uselist=False)
    audio_analysis = relationship("AudioAnalysis", back_populates="track", uselist=False)
    saved_by_users = relationship("SavedTrack", back_populates="track")
    top_for_users = relationship("UserTopTrack", back_populates="track")

class Playlist(Base):
    __tablename__ = 'playlists'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    public = Column(Boolean)
    collaborative = Column(Boolean)
    followers_total = Column(Integer)
    snapshot_id = Column(String)
    spotify_url = Column(String)
    href = Column(String)
    uri = Column(String)
    images = Column(Text)  # JSON string of images list
    primary_color = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign Keys
    owner_id = Column(String, ForeignKey('users.id'))
    
    # Relationships
    owner = relationship("User", back_populates="playlists")
    tracks = relationship("Track", secondary=playlist_track_association, back_populates="playlists")

class AudioFeatures(Base):
    __tablename__ = 'audio_features'
    
    track_id = Column(String, ForeignKey('tracks.id'), primary_key=True)
    danceability = Column(Float)
    energy = Column(Float)
    key = Column(Integer)
    loudness = Column(Float)
    mode = Column(Integer)
    speechiness = Column(Float)
    acousticness = Column(Float)
    instrumentalness = Column(Float)
    liveness = Column(Float)
    valence = Column(Float)
    tempo = Column(Float)
    time_signature = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    track = relationship("Track", back_populates="audio_features")

class AudioAnalysis(Base):
    __tablename__ = 'audio_analysis'
    
    track_id = Column(String, ForeignKey('tracks.id'), primary_key=True)
    bars = Column(Text)  # JSON string
    beats = Column(Text)  # JSON string
    sections = Column(Text)  # JSON string
    segments = Column(Text)  # JSON string
    tatums = Column(Text)  # JSON string
    track_analysis = Column(Text)  # JSON string of track-level analysis
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    track = relationship("Track", back_populates="audio_analysis")

class SavedTrack(Base):
    __tablename__ = 'saved_tracks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    track_id = Column(String, ForeignKey('tracks.id'), nullable=False)
    added_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="saved_tracks")
    track = relationship("Track", back_populates="saved_by_users")

class UserTopTrack(Base):
    __tablename__ = 'user_top_tracks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    track_id = Column(String, ForeignKey('tracks.id'), nullable=False)
    time_range = Column(String)  # short_term, medium_term, long_term
    rank = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="top_tracks")
    track = relationship("Track", back_populates="top_for_users")

class UserTopArtist(Base):
    __tablename__ = 'user_top_artists'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, ForeignKey('users.id'), nullable=False)
    artist_id = Column(String, ForeignKey('artists.id'), nullable=False)
    time_range = Column(String)  # short_term, medium_term, long_term
    rank = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="top_artists")
    artist = relationship("Artist", back_populates="top_for_users")
