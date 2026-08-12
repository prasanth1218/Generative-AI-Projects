from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config.settings import settings
from backend.db.models import Base

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Create tables if they don't exist. Fine for a 2-day build;
    swap for Alembic migrations in a real production rollout."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """FastAPI dependency -- yields a session per request, closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
