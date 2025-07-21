"""
Database initialization script for Spotify MusiVault.
Run this script to create the database and tables.
"""

import sys
import os
from sqlalchemy import create_engine

# Add the app directory to the Python path
project_root = os.path.dirname(__file__)
app_dir = os.path.join(project_root, 'app')
sys.path.insert(0, app_dir)

# Import models
from models import Base

def init_database():
    """Initialize the database by creating all tables."""
    # Create SQLite database in the project root
    db_path = os.path.join(project_root, 'spotify_data.db')
    database_url = f'sqlite:///{db_path}'
    
    print(f"Creating database at: {db_path}")
    print(f"Database URL: {database_url}")
    
    # Create engine and tables
    engine = create_engine(database_url, echo=True)
    Base.metadata.create_all(bind=engine)
    
    print(f"Database created successfully at: {db_path}")
    
    # Verify the file exists
    if os.path.exists(db_path):
        size = os.path.getsize(db_path)
        print(f"✓ Database file verified! Size: {size} bytes")
    else:
        print("✗ Database file not found after creation")

if __name__ == '__main__':
    print("=" * 60)
    print("Initializing Spotify MusiVault database...")
    print("=" * 60)
    
    try:
        init_database()
        print("=" * 60)
        print("Database initialization complete!")
        print("=" * 60)
    except Exception as e:
        print(f"Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
