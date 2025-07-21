"""
Simple test to create database and check models
"""

import sys
import os

# Add paths
project_root = os.path.dirname(__file__)
app_dir = os.path.join(project_root, 'app')
sys.path.insert(0, app_dir)

print("Starting database test...")

try:
    from models import Base, User, Artist, Album, Track
    print("✓ Models imported successfully")
    
    from sqlalchemy import create_engine
    print("✓ SQLAlchemy imported successfully")
    
    # Create database
    db_path = os.path.join(project_root, 'spotify_data.db')
    database_url = f'sqlite:///{db_path}'
    print(f"Database URL: {database_url}")
    
    engine = create_engine(database_url, echo=True)
    print("✓ Engine created")
    
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created")
    
    print(f"Database file should be at: {db_path}")
    
    if os.path.exists(db_path):
        print("✓ Database file exists!")
        print(f"File size: {os.path.getsize(db_path)} bytes")
    else:
        print("✗ Database file not found")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
