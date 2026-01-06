from typing import Optional
from fastapi import Depends, HTTPException, Header, status
from .config import settings


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    if not settings.api_key_enabled:
        return True
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key required"
        )
    
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return True
