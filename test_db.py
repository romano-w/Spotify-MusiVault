"""
Simple test to create database and check models
"""

import sys
import os

# Ensure the project root is on the Python path for package imports
project_root = os.path.dirname(__file__)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

print("Starting database test...")

try:
    from app.models import Base, User, Artist, Album, Track
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
