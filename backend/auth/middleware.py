"""
Authentication Middleware
JWT validation and user context
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict, Optional

from backend.config.settings import settings

security = HTTPBearer()


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> Dict:
    """
    Get current user from JWT token
    
    For testing, returns a mock user if no token provided
    """
    # For development/testing without auth
    if not credentials and settings.ENVIRONMENT == "development":
        return {
            "username": "test_user",
            "account_id": 123,
            "email": "test@webconnex.com",
            "roles": ["user"]
        }
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    try:
        # Decode JWT token
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        return {
            "username": payload.get("sub"),
            "account_id": payload.get("account_id"),
            "email": payload.get("email"),
            "roles": payload.get("roles", ["user"])
        }
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )