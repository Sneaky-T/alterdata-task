import os
from fastapi import FastAPI, Depends
from app.api.transactions import transactions_router
from app.api.reports import reports_router
from app.utils.log_utils import setup_logging
from app.utils.auth_utils import verify_api_key
from dotenv import load_dotenv

load_dotenv()

setup_logging()

app = FastAPI()


@app.get("/")
def root() -> dict[str, str]:
    return {"message": "Welcome!"}


app.include_router(transactions_router, dependencies=[Depends(verify_api_key)])
app.include_router(reports_router, dependencies=[Depends(verify_api_key)])

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
