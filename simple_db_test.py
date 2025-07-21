"""
Simple database creation script
"""
import os
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class TestUser(Base):
    __tablename__ = 'test_users'
    
    id = Column(String, primary_key=True)
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

if __name__ == '__main__':
    try:
        print("=" * 50)
        print("Creating simple test database...")
        print("=" * 50)
        
        # Create database
        db_path = os.path.join(os.path.dirname(__file__), 'test_spotify_data.db')
        database_url = f'sqlite:///{db_path}'
        
        print(f"Database URL: {database_url}")
        print(f"Database path: {db_path}")
        
        engine = create_engine(database_url, echo=True)
        print("Engine created successfully")
        
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully")
        
        print(f"Database should be at: {db_path}")
        
        if os.path.exists(db_path):
            size = os.path.getsize(db_path)
            print(f"✓ Database file exists! Size: {size} bytes")
        else:
            print("✗ Database file not created")
            
        print("=" * 50)
        print("Test completed")
        print("=" * 50)
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
