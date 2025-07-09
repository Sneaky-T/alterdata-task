import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from app.api.transactions import transactions_router
from app.api.reports import reports_router
from app.utils.log_utils import setup_logging
from app.utils.auth_utils import verify_api_key
from dotenv import load_dotenv
from app.utils.db_utils import ensure_tables_exist
import logging
from collections.abc import AsyncGenerator

load_dotenv()
setup_logging()
logger = logging.getLogger(__name__)


HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    logger.info("Starting application...")
    ensure_tables_exist()
    logger.info("Application startup complete")
    yield
    logger.info("Application shutdown complete")


app = FastAPI(lifespan=lifespan)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome!"}


app.include_router(transactions_router, dependencies=[Depends(verify_api_key)])
app.include_router(reports_router, dependencies=[Depends(verify_api_key)])
