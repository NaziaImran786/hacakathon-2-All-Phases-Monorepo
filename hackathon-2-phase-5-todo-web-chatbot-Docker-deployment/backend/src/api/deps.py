# JWT Authentication Dependencies for Phase III Chatbot
# Task ID: T014
# Reference: specs/features/chatbot/plan.md (JWT Authentication Integration)
# Reference: .specify/memory/constitution.md (Principles IV, V, VII)

import uuid
import os
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from pydantic import BaseModel


# HTTP Bearer token scheme for JWT
security = HTTPBearer()


class TokenPayload(BaseModel):
    """JWT token payload structure."""
    sub: str  # User ID (UUID)
    email: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None


async def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    Extract and verify JWT token, return user_id.

    This dependency is used by all API endpoints that require authentication.
    It extracts the user_id from the JWT's "sub" claim, which is used for:
    - Database query filtering (user isolation)
    - MCP tool parameter injection
    - Audit logging

    NOTE: Phase I/II auth uses username as sub claim, not UUID.
    We accept both formats for backward compatibility.

    Returns:
        str: The user identifier from the JWT token (username or UUID)

    Raises:
        HTTPException: 401 if token is invalid, expired, or missing user_id
    """
    token: str = credentials.credentials
    # Use same fallback as auth.py for consistency
    secret: str = os.getenv("BETTER_AUTH_SECRET", "fallback-secret-for-dev")

    try:
        # Verify and decode JWT token
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={
                "verify_exp": True,
                "verify_iat": True,
            }
        )

        # Extract user_id from "sub" claim
        # Phase I/II uses username, Phase III may use UUID - accept both
        user_id: str = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user_id (sub claim)",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Accept any non-empty string as user_id (username or UUID)
        if not user_id.strip():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id cannot be empty",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return user_id

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


def create_access_token(
    user_id: str,
    email: Optional[str] = None,
    expires_delta: Optional[int] = None
) -> str:
    """
    Create a JWT access token (for testing purposes).

    Args:
        user_id: The user's UUID
        email: Optional email address
        expires_delta: Optional expiration time in seconds (default: 24 hours)

    Returns:
        str: Encoded JWT token
    """
    import time

    secret: str = os.getenv("BETTER_AUTH_SECRET", "fallback-secret-for-dev")
    expires_delta = expires_delta or 86400  # 24 hours

    payload = {
        "sub": user_id,
        "iat": int(time.time()),
        "exp": int(time.time()) + expires_delta,
    }

    if email:
        payload["email"] = email

    return jwt.encode(payload, secret, algorithm="HS256")


def decode_token(token: str) -> TokenPayload:
    """
    Decode a JWT token without verification (for debugging).

    Args:
        token: The JWT token string

    Returns:
        TokenPayload: Decoded token payload
    """
    secret: str = os.getenv("BETTER_AUTH_SECRET", "fallback-secret-for-dev")

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            options={"verify_exp": False}
        )
        return TokenPayload(**payload)
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")
