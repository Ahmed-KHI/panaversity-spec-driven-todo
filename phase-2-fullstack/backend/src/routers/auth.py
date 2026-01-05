"""
Authentication endpoints (register, login).
[Task]: T-009 (Auth Endpoints)
[From]: spec.md §6.1, plan.md §7
"""

from fastapi import APIRouter, HTTPException, status, Depends
from sqlmodel import Session, select
from src.database import get_session
from src.models.user import User
from src.schemas.auth import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse
)
from src.utils.security import hash_password, verify_password, create_access_token
from src.config import settings

router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterRequest,
    session: Session = Depends(get_session)
):
    """
    Register new user account.
    
    - Email must be unique
    - Password minimum 8 characters
    - Returns user information
    """
    # Check if email already exists
    existing_user = session.exec(
        select(User).where(User.email == request.email)
    ).first()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists"
        )
    
    # Hash password
    password_hash = hash_password(request.password)
    
    # Create user
    user = User(
        email=request.email,
        password_hash=password_hash
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return RegisterResponse(
        id=user.id,
        email=user.email,
        message="Account created successfully"
    )


@router.post("/login", response_model=LoginResponse)
def login(
    request: LoginRequest,
    session: Session = Depends(get_session)
):
    """
    Login with email and password.
    
    Returns JWT token valid for 7 days.
    """
    # Get user by email
    user = session.exec(
        select(User).where(User.email == request.email)
    ).first()
    
    # Verify user exists and password is correct
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Generate JWT token
    access_token = create_access_token(
        user_id=user.id,
        email=user.email,
        secret_key=settings.BETTER_AUTH_SECRET
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user={
            "id": str(user.id),
            "email": user.email
        }
    )
