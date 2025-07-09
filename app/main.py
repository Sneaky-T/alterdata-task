from fastapi import FastAPI
from app.api.transactions import transactions_router
from app.api.reports import reports_router
from app.utils.log_utils import setup_logging

setup_logging()

app = FastAPI()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome!"}


app.include_router(transactions_router)
app.include_router(reports_router)
