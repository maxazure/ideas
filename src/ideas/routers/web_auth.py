"""Web authentication router with JWT tokens."""
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import APIRouter, HTTPException, status, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel

from ..config import settings

router = APIRouter()
security = HTTPBearer(auto_error=False)


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class UserInfo(BaseModel):
    username: str


def create_token(username: str) -> tuple[str, int]:
    """Create a JWT token with expiration."""
    expires_delta = timedelta(days=settings.jwt_expire_days)
    expires_at = datetime.now(timezone.utc) + expires_delta
    
    payload = {
        "sub": username,
        "exp": expires_at,
        "iat": datetime.now(timezone.utc)
    }
    
    token = jwt.encode(payload, settings.jwt_secret, algorithm="HS256")
    return token, int(expires_delta.total_seconds())


def verify_token(token: str) -> Optional[str]:
    """Verify JWT token and return username if valid."""
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload.get("sub")
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> str:
    """Dependency to get current authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    username = verify_token(credentials.credentials)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return username


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return JWT token."""
    if request.username != settings.web_username or request.password != settings.web_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    token, expires_in = create_token(request.username)
    return LoginResponse(access_token=token, expires_in=expires_in)


@router.get("/me", response_model=UserInfo)
async def get_me(username: str = Depends(get_current_user)):
    """Get current user info."""
    return UserInfo(username=username)


@router.get("/verify")
async def verify(username: str = Depends(get_current_user)):
    """Verify if token is still valid."""
    return {"valid": True, "username": username}
