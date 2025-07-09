import os
from typing import Optional
from fastapi import Header, HTTPException
import logging

logger = logging.getLogger(__name__)

API_KEY = os.getenv("API_KEY", "secret-key")


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if x_api_key != API_KEY:
        logger.warning(f"Invalid API key attempt: {x_api_key}")
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API Key.",
        )
