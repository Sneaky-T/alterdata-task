import os
from fastapi import Header, HTTPException, status

API_KEY = os.getenv("API_KEY", "secret-key")


async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key.",
        )
