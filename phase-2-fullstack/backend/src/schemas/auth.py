"""
Authentication request/response schemas.
[Task]: T-005 (User Schemas)
[From]: spec.md §6.1, plan.md §5
"""

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from typing import Dict


class RegisterRequest(BaseModel):
    """User registration request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="Password (min 8 characters)")


class RegisterResponse(BaseModel):
    """User registration response."""
    id: UUID
    email: str
    message: str = "Account created successfully"
    
    model_config = ConfigDict(from_attributes=True)


class LoginRequest(BaseModel):
    """User login request."""
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class LoginResponse(BaseModel):
    """User login response with JWT token."""
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: Dict[str, str] = Field(..., description="User information")
