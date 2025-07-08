import logging

from app.db import Base, engine
from app.models import transaction

from app.main import setup_logging


if __name__ == "__main__":
    setup_logging()
    Base.metadata.create_all(bind=engine)
    logging.info("Table created successfully.")
