"""
Database utility functions for the Eigen models package.

This module contains utility functions for database operations,
connection management, and common database patterns.
"""

from typing import Optional
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from ..base import Base


def create_database_engine(
    database_url: str,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
    **kwargs
):
    """
    Create a SQLAlchemy database engine with standard configuration.
    
    Args:
        database_url: Database connection URL
        echo: Whether to echo SQL queries (for debugging)
        pool_size: Size of the connection pool
        max_overflow: Maximum number of connections that can overflow the pool
        **kwargs: Additional engine configuration
    
    Returns:
        SQLAlchemy Engine instance
    """
    engine_kwargs = {
        "echo": echo,
        "pool_pre_ping": True,
        **kwargs
    }
    
    # Add pool configuration for non-SQLite databases
    if not database_url.startswith("sqlite"):
        engine_kwargs.update({
            "pool_size": pool_size,
            "max_overflow": max_overflow,
        })
    else:
        # SQLite-specific configuration
        engine_kwargs.update({
            "poolclass": StaticPool,
            "connect_args": {"check_same_thread": False},
        })
    
    return create_engine(database_url, **engine_kwargs)


def create_session_factory(engine):
    """
    Create a SQLAlchemy session factory.
    
    Args:
        engine: SQLAlchemy Engine instance
    
    Returns:
        SQLAlchemy sessionmaker factory
    """
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine
    )


def get_database_session(session_factory) -> Session:
    """
    Get a database session from the session factory.
    
    Args:
        session_factory: SQLAlchemy sessionmaker factory
    
    Returns:
        SQLAlchemy Session instance
    """
    return session_factory()


def create_all_tables(engine):
    """
    Create all tables defined in the Eigen models.
    
    Args:
        engine: SQLAlchemy Engine instance
    """
    Base.metadata.create_all(bind=engine)


def drop_all_tables(engine):
    """
    Drop all tables defined in the Eigen models.
    
    Warning: This will delete all data!
    
    Args:
        engine: SQLAlchemy Engine instance
    """
    Base.metadata.drop_all(bind=engine)


class DatabaseManager:
    """
    Database manager for Eigen models.
    
    Provides a convenient interface for database operations with
    automatic session management and connection handling.
    """
    
    def __init__(self, database_url: str, **engine_kwargs):
        """
        Initialize the database manager.
        
        Args:
            database_url: Database connection URL
            **engine_kwargs: Additional engine configuration
        """
        self.database_url = database_url
        self.engine = create_database_engine(database_url, **engine_kwargs)
        self.session_factory = create_session_factory(self.engine)
    
    def get_session(self) -> Session:
        """Get a new database session."""
        return get_database_session(self.session_factory)
    
    def create_tables(self):
        """Create all tables."""
        create_all_tables(self.engine)
    
    def drop_tables(self):
        """Drop all tables (WARNING: deletes all data!)."""
        drop_all_tables(self.engine)
    
    def close(self):
        """Close the database engine."""
        self.engine.dispose()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Example usage patterns
def example_usage():
    """
    Example usage of the database utilities.
    
    This function demonstrates how to use the database utilities
    in a typical Eigen application.
    """
    # Basic engine and session setup
    database_url = "postgresql://user:password@localhost/eigen_db"
    engine = create_database_engine(database_url)
    session_factory = create_session_factory(engine)
    
    # Create tables
    create_all_tables(engine)
    
    # Use session
    with get_database_session(session_factory) as session:
        # Your database operations here
        pass
    
    # Using the DatabaseManager
    with DatabaseManager(database_url) as db:
        db.create_tables()
        
        with db.get_session() as session:
            # Your database operations here
            pass