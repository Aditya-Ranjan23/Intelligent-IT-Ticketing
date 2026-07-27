import logging
from typing import Generator

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

logger = logging.getLogger(__name__)

# Primary database URL
db_url = settings.POSTGRES_URI

# Fallback to SQLite if Postgres is unavailable in simple local runs without docker
try:
    engine = create_engine(db_url, pool_pre_ping=True, echo=False)
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
        conn.commit()
    logger.info("Successfully connected to PostgreSQL with pgvector extension enabled.")
except Exception as e:
    logger.warning(f"Could not connect to PostgreSQL ({e}). Falling back to SQLite file database.")
    fallback_url = "sqlite:///./it_ticketing.db"
    engine = create_engine(fallback_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables in database."""
    Base.metadata.create_all(bind=engine)
