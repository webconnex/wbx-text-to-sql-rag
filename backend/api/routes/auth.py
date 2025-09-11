"""
Authentication Routes
Handles Okta SSO and token management
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
from datetime import datetime, timedelta
import jwt

from backend.config.settings import settings

router = APIRouter()


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str
    account_id: int


class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest) -> TokenResponse:
    """
    Login endpoint (temporary - will be replaced with Okta)
    
    For testing only - generates a JWT token
    """
    # TODO: Implement Okta authentication
    # For now, create a test token
    
    payload = {
        "sub": request.username,
        "account_id": request.account_id,
        "exp": datetime.utcnow() + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
        "iat": datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return TokenResponse(
        access_token=token,
        expires_in=settings.JWT_EXPIRATION_MINUTES * 60
    )


@router.post("/logout")
async def logout() -> Dict[str, str]:
    """
    Logout endpoint
    """
    # TODO: Implement token revocation
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user() -> Dict[str, Any]:
    """
    Get current user information
    """
    # TODO: Implement with real user data
    return {
        "username": "test_user",
        "account_id": 123,
        "email": "test@webconnex.com",
        "roles": ["user"]
    }