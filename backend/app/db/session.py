import logging
from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import get_settings
from app.db.base import Base

logger = logging.getLogger("actp.db")

_engine = None
_SessionFactory = None
_active_engine_name = "unknown"

def get_engine():
    global _engine, _active_engine_name
    if _engine is not None:
        return _engine

    settings = get_settings()
    primary_url = settings.DATABASE_URL
    fallback_url = settings.SQLITE_FALLBACK_URL

    # Attempt PostgreSQL connection
    try:
        logger.info(f"Connecting to primary database: {primary_url.split('@')[-1] if '@' in primary_url else primary_url}")
        test_engine = create_engine(
            primary_url,
            pool_pre_ping=True,
            connect_args={"connect_timeout": 3} if "postgresql" in primary_url else {}
        )
        with test_engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Successfully connected to primary PostgreSQL database.")
        _engine = test_engine
        _active_engine_name = "postgresql"
    except Exception as e:
        logger.warning(
            f"Primary database connection failed ({e}). "
            f"Falling back to local SQLite: {fallback_url}"
        )
        _engine = create_engine(
            fallback_url,
            connect_args={"check_same_thread": False} if "sqlite" in fallback_url else {}
        )
        _active_engine_name = "sqlite"

    return _engine

def get_session_factory():
    global _SessionFactory
    if _SessionFactory is None:
        engine = get_engine()
        _SessionFactory = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionFactory

def get_active_engine_name() -> str:
    get_engine()
    return _active_engine_name

def init_db():
    """Initializes schema tables if not existing."""
    engine = get_engine()
    logger.info(f"Creating all tables using active engine ({_active_engine_name})...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables initialized successfully.")

def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session."""
    factory = get_session_factory()
    session = factory()
    try:
        yield session
    finally:
        session.close()
