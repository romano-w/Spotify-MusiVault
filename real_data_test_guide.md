# 🎵 Real Data Testing Guide - Spotify MusiVault

## 🚀 Getting Started

Your Flask server should now be running at: **http://127.0.0.1:5000**

## 📋 Testing Steps

### 1. **Open the Web Interface**
- Navigate to: `http://127.0.0.1:5000`
- You should see a "Login with Spotify" button

### 2. **Authorize with Spotify**
- Click "Login with Spotify"
- You'll be redirected to Spotify's authorization page
- Log in with your Spotify account
- Grant the necessary permissions:
  - Read your private playlists
  - Read your saved tracks
  - Read your top artists and tracks
  - Read your followed artists

### 3. **Data Collection Process**
After authorization, the system will automatically:
- ✅ Collect your user profile data
- ✅ Gather all your playlists (private and public)
- ✅ Store all tracks from your playlists with full metadata
- ✅ Collect your saved tracks (liked songs)
- ✅ Get your top artists and tracks
- ✅ Fetch audio features for all tracks
- ✅ Link all relationships (artists ↔ tracks ↔ albums ↔ playlists)

### 4. **Expected Results**
You'll see a completion page with statistics like:
```
🎉 Data Collection Complete!

📊 Collection Results:
- Users stored: 1
- Artists stored: X
- Albums stored: X
- Tracks stored: X
- Playlists stored: X
- Audio Features stored: X
- Relationships mapped: X
```

## 🔍 What Gets Stored

### **User Data**
- Profile information (username, display name, follower count)
- Spotify ID and external URLs

### **Playlists**
- All your playlists (name, description, track count)
- Playlist metadata (collaborative, public status)
- Full track listings with positions

### **Tracks**
- Complete track metadata (name, duration, popularity, preview URL)
- Album information
- Artist relationships
- Audio features (danceability, energy, valence, etc.)

### **Artists**
- Artist profiles and metadata
- Popularity and follower counts
- Genres and external URLs

### **Albums**
- Album details (name, release date, total tracks)
- Album types (album, single, compilation)
- Cover art URLs

## 📊 Database Monitoring

### Check Collection Progress
Visit: `http://127.0.0.1:5000/db-stats`

This endpoint returns real-time database statistics in JSON format.

### Database File
Your data is stored in: `spotify_data.db` (SQLite database)

## 🛠️ Troubleshooting

### Common Issues:

1. **"Authorization Error"**
   - Ensure your Spotify app credentials are correct in `.env`
   - Check that the redirect URI matches: `http://127.0.0.1:5000/authorize`

2. **"Database Error"**
   - The database should auto-initialize
   - Check file permissions in the project directory

3. **"Rate Limiting"**
   - Spotify API has rate limits
   - The system includes automatic retry logic
   - Large collections may take several minutes

### Expected Collection Times:
- Small collection (< 500 tracks): 1-2 minutes
- Medium collection (500-2000 tracks): 3-8 minutes  
- Large collection (2000+ tracks): 10+ minutes

## 🎯 Testing Checklist

- [ ] Flask server starts without errors
- [ ] Can access login page at `http://127.0.0.1:5000`
- [ ] Spotify authorization flows works
- [ ] Data collection completes successfully
- [ ] Statistics page shows collected data
- [ ] Database file (`spotify_data.db`) grows in size
- [ ] No errors in the Flask console output

## 🔍 Advanced Testing

### Manual Database Inspection
```python
# In a Python shell within the Poetry environment:
from app.database import db_session
from app.models import User, Track, Playlist, Artist

with db_session() as session:
    # Check user count
    user_count = session.query(User).count()
    print(f"Users: {user_count}")
    
    # Check track count
    track_count = session.query(Track).count()
    print(f"Tracks: {track_count}")
    
    # Check playlist count
    playlist_count = session.query(Playlist).count()
    print(f"Playlists: {playlist_count}")
```

## 🚀 Ready for Real Data!

Your system is now ready to collect and store your actual Spotify data. The complete pipeline from web authorization to database storage is operational!

**Happy testing!** 🎉
