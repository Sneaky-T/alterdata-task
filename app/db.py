import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from typing import Generator
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
import logging

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql+psycopg2://admin:secret@localhost:5432/transactions_db"
)

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    try:
        db = SessionLocal()
    except (SQLAlchemyError, OperationalError) as e:
        logger.error(f"Database session creation failed: {type(e).__name__}: {e}")
        raise RuntimeError(f"Database session creation failed: {type(e).__name__}: {e}")
    except Exception as e:
        logger.exception("Unexpected error during session creation")
        raise RuntimeError(
            f"Unexpected error during session creation: {type(e).__name__}: {e}"
        )

    try:
        yield db
    finally:
        db.close()
