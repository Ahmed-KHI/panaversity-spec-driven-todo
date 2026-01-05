"""
JWT and password hashing utilities.
[Task]: T-007 (Security Utilities)
[From]: spec.md §8, plan.md §6
"""

import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
from uuid import UUID


def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(
        plain_password.encode('utf-8'),
        hashed_password.encode('utf-8')
    )


def create_access_token(
    user_id: UUID,
    email: str,
    secret_key: str,
    expires_delta: timedelta = timedelta(days=7)
) -> str:
    """Create JWT access token."""
    expire = datetime.utcnow() + expires_delta
    to_encode = {
        "user_id": str(user_id),
        "email": email,
        "exp": expire,
        "iat": datetime.utcnow()
    }
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm="HS256")
    return encoded_jwt


def verify_token(token: str, secret_key: str) -> Optional[Dict]:
    """Verify and decode JWT token (compatible with Better Auth tokens)."""
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        
        # Better Auth tokens use 'userId' instead of 'user_id'
        # Support both formats for compatibility
        user_id = payload.get("userId") or payload.get("user_id")
        email = payload.get("email")
        
        if not user_id or not email:
            return None
            
        # Normalize payload format
        return {
            "user_id": user_id,
            "email": email,
            "exp": payload.get("exp"),
            "iat": payload.get("iat")
        }
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
    except Exception:
        return None  # Any other error
