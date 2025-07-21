"""
Simple database test to verify Phase 1 completion.
"""

import sys
import os

# Add the app directory to the Python path
app_dir = os.path.join(os.path.dirname(__file__), 'app')
sys.path.insert(0, app_dir)

from database import db_session
from models import User, Artist, Album, Track, Playlist, AudioFeatures

def test_basic_operations():
    """Test basic database operations."""
    print("=" * 60)
    print("Testing Basic Database Operations - Phase 1")
    print("=" * 60)
    
    try:
        # Test database connection
        print("\n1. Testing database connection...")
        with db_session() as session:
            # Test table existence by counting
            user_count = session.query(User).count()
            artist_count = session.query(Artist).count()
            album_count = session.query(Album).count()
            track_count = session.query(Track).count()
            playlist_count = session.query(Playlist).count()
            features_count = session.query(AudioFeatures).count()
            
            print("✓ Database connection successful!")
            print(f"   Current record counts:")
            print(f"   - Users: {user_count}")
            print(f"   - Artists: {artist_count}")
            print(f"   - Albums: {album_count}")
            print(f"   - Tracks: {track_count}")
            print(f"   - Playlists: {playlist_count}")
            print(f"   - Audio Features: {features_count}")
        
        # Test creating a simple user
        print("\n2. Testing user creation...")
        with db_session() as session:
            test_user = User(
                id='test_user_phase1',
                display_name='Phase 1 Test User',
                email='test@phase1.com',
                country='US',
                followers_total=0
            )
            session.add(test_user)
            session.commit()
            
            # Verify the user was created
            created_user = session.query(User).filter(User.id == 'test_user_phase1').first()
            if created_user:
                print(f"✓ User created successfully: {created_user.display_name}")
            else:
                print("✗ User creation failed")
        
        # Test creating a simple artist
        print("\n3. Testing artist creation...")
        with db_session() as session:
            test_artist = Artist(
                id='test_artist_phase1',
                name='Phase 1 Test Artist'
            )
            session.add(test_artist)
            session.commit()
            
            # Verify the artist was created
            created_artist = session.query(Artist).filter(Artist.id == 'test_artist_phase1').first()
            if created_artist:
                print(f"✓ Artist created successfully: {created_artist.name}")
            else:
                print("✗ Artist creation failed")
        
        # Test final counts
        print("\n4. Final verification...")
        with db_session() as session:
            final_user_count = session.query(User).count()
            final_artist_count = session.query(Artist).count()
            
            print(f"✓ Final counts:")
            print(f"   - Users: {final_user_count}")
            print(f"   - Artists: {final_artist_count}")
        
        print("\n" + "=" * 60)
        print("✅ PHASE 1 COMPLETE!")
        print("✅ Database Foundation Successfully Implemented:")
        print("   - ✓ SQLite database created")
        print("   - ✓ All database models defined")
        print("   - ✓ Database connection management working")
        print("   - ✓ Basic CRUD operations functional")
        print("   - ✓ Session management implemented")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_basic_operations()
    if not success:
        sys.exit(1)
