import logging
import os
import sys


def setup_logging() -> None:
    try:
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
    except (OSError, PermissionError, IOError) as e:
        print(f"Failed to set up logging: {type(e).__name__}: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(
            f"Unexpected error during logging setup: {type(e).__name__}: {e}",
            file=sys.stderr,
        )
        sys.exit(1)
