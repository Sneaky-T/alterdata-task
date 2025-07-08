from fastapi import FastAPI
import logging
import os
from app.api.transactions import transactions_router


def setup_logging() -> None:
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
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


setup_logging()

app = FastAPI()

app.include_router(transactions_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome!"}
