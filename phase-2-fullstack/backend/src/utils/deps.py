"""
Dependency injection for FastAPI.
[Task]: T-008 (Dependencies)
[From]: spec.md §8, plan.md §6
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from uuid import UUID
from src.database import get_session
from src.models.user import User
from src.utils.security import verify_token
from src.config import settings

# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Extract and verify JWT token, return authenticated user.
    
    Raises:
        HTTPException: 401 if token invalid or user not found
    """
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token, settings.BETTER_AUTH_SECRET)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Extract user_id from token
    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    # Get user from database
    user = session.get(User, UUID(user_id))
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user
