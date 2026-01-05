"""Database session and connection management."""

from sqlmodel import Session, create_engine
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()


@lru_cache
def get_database_url() -> str:
    """Get database URL from environment variable."""
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL environment variable is not set")
    
    # Convert postgresql:// to postgresql+psycopg:// for psycopg3
    if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    return database_url


@lru_cache
def get_engine():
    """Create and cache database engine."""
    database_url = get_database_url()
    engine = create_engine(database_url, echo=False)
    return engine


def get_session():
    """Get a new database session."""
    engine = get_engine()
    with Session(engine) as session:
        yield session


def get_sync_session() -> Session:
    """Get a synchronous database session (for MCP server)."""
    engine = get_engine()
    return Session(engine)


def init_db():
    """Initialize the database by creating all tables."""
    from app.models.task import Task  # noqa: F401
    from sqlmodel import SQLModel
    
    engine = get_engine()
    SQLModel.metadata.create_all(engine)
