"""
Simple API-key auth. Kept intentionally basic for a 2-day build -- in
the live round, be upfront that this is a stand-in for a real auth system
(JWT + user table already exist in db/models.py) and that swapping this
dependency for real OAuth/JWT validation doesn't touch any other file.
Traditional software logic, not AI -- see Q48.
"""
from fastapi import Header, HTTPException, status

from backend.config.settings import settings


def verify_api_key(x_api_key: str = Header(default="")):
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return True
