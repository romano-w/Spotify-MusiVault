"""
CSV export utility for core Spotify MusiVault tables.
Usage:
  poetry run python -m app.export_data --out ./exports
"""

import csv
import os
from argparse import ArgumentParser
from typing import Iterable

from database import db_session
from models import User, Artist, Album, Track, Playlist, AudioFeatures, AudioAnalysis, SavedTrack, UserTopTrack, UserTopArtist


def rows_to_csv(path: str, rows: Iterable[dict]):
    rows = list(rows)
    if not rows:
        return
    fieldnames = sorted({k for r in rows for k in r.keys()})
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def export_all(out_dir: str):
    with db_session() as session:
        print(f"Exporting to {out_dir}...")
        # Users
        rows_to_csv(os.path.join(out_dir, 'users.csv'), (
            {
                'id': u.id,
                'display_name': u.display_name,
                'email': u.email,
                'country': u.country,
                'followers_total': u.followers_total,
                'product': u.product,
                'created_at': u.created_at,
                'updated_at': u.updated_at,
            } for u in session.query(User).all()
        ))

        # Artists
        rows_to_csv(os.path.join(out_dir, 'artists.csv'), (
            {
                'id': a.id,
                'name': a.name,
                'genres': a.genres,
                'popularity': a.popularity,
                'followers_total': a.followers_total,
            } for a in session.query(Artist).all()
        ))

        # Albums
        rows_to_csv(os.path.join(out_dir, 'albums.csv'), (
            {
                'id': al.id,
                'name': al.name,
                'album_type': al.album_type,
                'release_date': al.release_date,
                'release_date_precision': al.release_date_precision,
                'total_tracks': al.total_tracks,
            } for al in session.query(Album).all()
        ))

        # Tracks
        rows_to_csv(os.path.join(out_dir, 'tracks.csv'), (
            {
                'id': t.id,
                'name': t.name,
                'album_id': t.album_id,
                'duration_ms': t.duration_ms,
                'explicit': t.explicit,
                'popularity': t.popularity,
            } for t in session.query(Track).all()
        ))

        # Playlists
        rows_to_csv(os.path.join(out_dir, 'playlists.csv'), (
            {
                'id': p.id,
                'name': p.name,
                'owner_id': p.owner_id,
                'collaborative': p.collaborative,
                'public': p.public,
                'followers_total': p.followers_total,
            } for p in session.query(Playlist).all()
        ))

        # Audio Features
        rows_to_csv(os.path.join(out_dir, 'audio_features.csv'), (
            {
                'track_id': af.track_id,
                'danceability': af.danceability,
                'energy': af.energy,
                'tempo': af.tempo,
                'valence': af.valence,
                'loudness': af.loudness,
                'acousticness': af.acousticness,
                'instrumentalness': af.instrumentalness,
            } for af in session.query(AudioFeatures).all()
        ))

        # Audio Analysis (track-level only for brevity)
        rows_to_csv(os.path.join(out_dir, 'audio_analysis.csv'), (
            {
                'track_id': aa.track_id,
                'track_analysis': aa.track_analysis,
            } for aa in session.query(AudioAnalysis).all()
        ))

        # Saved Tracks
        rows_to_csv(os.path.join(out_dir, 'saved_tracks.csv'), (
            {
                'id': st.id,
                'user_id': st.user_id,
                'track_id': st.track_id,
                'added_at': st.added_at,
            } for st in session.query(SavedTrack).all()
        ))

        # Top items
        rows_to_csv(os.path.join(out_dir, 'user_top_tracks.csv'), (
            {
                'id': utt.id,
                'user_id': utt.user_id,
                'track_id': utt.track_id,
                'time_range': utt.time_range,
                'rank': utt.rank,
            } for utt in session.query(UserTopTrack).all()
        ))

        rows_to_csv(os.path.join(out_dir, 'user_top_artists.csv'), (
            {
                'id': uta.id,
                'user_id': uta.user_id,
                'artist_id': uta.artist_id,
                'time_range': uta.time_range,
                'rank': uta.rank,
            } for uta in session.query(UserTopArtist).all()
        ))

        print("✅ Export complete")


def main():
    parser = ArgumentParser()
    parser.add_argument('--out', required=True, help='Output directory for CSV files')
    args = parser.parse_args()
    export_all(args.out)


if __name__ == '__main__':
    main()
