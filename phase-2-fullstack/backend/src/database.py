"""
Database connection and session management.
[Task]: T-004 (Database Setup)
[From]: spec.md §7, plan.md §4
"""

from sqlmodel import create_engine, SQLModel, Session
from src.config import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=True if settings.ENVIRONMENT == "development" else False,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)


def create_db_and_tables():
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """
    Dependency to get database session.
    
    Yields:
        Session: SQLModel database session
    """
    with Session(engine) as session:
        yield session
