from fastapi import FastAPI
from app.api.transactions import transactions_router
from app.utils.log_utils import setup_logging


setup_logging()

app = FastAPI()

app.include_router(transactions_router)


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome!"}
