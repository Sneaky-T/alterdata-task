from sqlalchemy.exc import OperationalError, ProgrammingError
from app.db import Base, engine
from app.models import transaction
import logging

logger = logging.getLogger(__name__)


def ensure_tables_exist() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables checked/created successfully")
    except (OperationalError, ProgrammingError) as e:
        logger.error(
            f"Database error during table check/creation: {type(e).__name__}: {e}"
        )
        raise RuntimeError(
            f"Database error during table check/creation: {type(e).__name__}: {e}"
        )
    except Exception as e:
        logger.exception("Unexpected error during table check/creation")
        raise RuntimeError(
            f"Unexpected error during table check/creation: {type(e).__name__}: {e}"
        )
