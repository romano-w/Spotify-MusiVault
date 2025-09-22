"""
Database connection and session management for Spotify MusiVault.
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
from .models import Base

class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self, database_url=None):
        if database_url is None:
            database_url = os.getenv('DATABASE_URL')

        if database_url is None:
            # Default to SQLite database in the project root
            db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'spotify_data.db')
            database_url = f'sqlite:///{db_path}'
        
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
    def create_tables(self):
        """Create all database tables."""
        Base.metadata.create_all(bind=self.engine)
        
    def drop_tables(self):
        """Drop all database tables."""
        Base.metadata.drop_all(bind=self.engine)
        
    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()
    
    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

# Global database manager instance
db_manager = DatabaseManager()

def init_database():
    """Initialize the database by creating all tables."""
    db_manager.create_tables()
    print("Database initialized successfully!")

def get_db_session():
    """Get a database session."""
    return db_manager.get_session()

@contextmanager
def db_session():
    """Context manager for database sessions."""
    with db_manager.session_scope() as session:
        yield session
