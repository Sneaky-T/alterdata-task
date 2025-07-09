import logging
import os


def setup_logging() -> None:
    os.makedirs("logs", exist_ok=True)
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("logs/debug.log"),
        ],
    )
    sql_logger = logging.getLogger("sqlalchemy.engine")
    sql_logger.propagate = False
    sql_logger.setLevel(logging.INFO)
    sql_logger.addHandler(logging.FileHandler("logs/sql.log"))
    logging.info("Logging setup complete.")
