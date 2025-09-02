import logging
import os

from fastapi import Request, HTTPException

from config import load_config

settings = load_config()
logger = logging.getLogger(__name__)
logger.setLevel(settings.log_level)

async def verify_token(request: Request):
    auth_header = request.headers.get("Authorization")
    if not auth_header or auth_header != f"Bearer {request.app.state.settings.token}":
        raise HTTPException(
            status_code=401,
            detail="Invalid or missing token",
        )


def remove_file_extension(filename: str) -> str:
    return os.path.splitext(filename)[0]
