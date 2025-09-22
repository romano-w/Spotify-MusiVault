# Real Data Testing Guide - Spotify MusiVault

## Getting Started

Your Flask server should run at: <http://127.0.0.1:5000>

## Testing Steps

1. Open <http://127.0.0.1:5000> and click "Login with Spotify"
2. Authorize with Spotify and grant permissions
3. After redirect, the app collects and stores your data

## What Gets Stored

- User profile
- Playlists and playlist tracks
- Tracks with album/artist links
- Saved tracks
- Top artists and tracks
- Audio features and analysis

## Monitoring

- View stats at: <http://127.0.0.1:5000/db-stats>
- SQLite file: `spotify_data.db`

## Troubleshooting

- Check `.env` has `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET`, `APP_SECRET_KEY`
- Redirect URI must include `/authorize`

## Advanced

Use Python shell:

from app.database import db_session
from app.models import User, Track, Playlist, Artist

with db_session() as s:
    print("Users:", s.query(User).count())
    print("Tracks:", s.query(Track).count())
    print("Playlists:", s.query(Playlist).count())
