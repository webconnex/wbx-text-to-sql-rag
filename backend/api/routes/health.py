"""
Health Check Routes
System health and status monitoring
"""

from fastapi import APIRouter, status
from datetime import datetime
from typing import Dict, Any

from backend.config.settings import settings
from backend.auth.aws_auth import aws_auth

router = APIRouter()


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "webconnex-text-to-sql",
        "version": "1.0.0"
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check - verifies all services are ready
    """
    checks = {
        "api": True,
        "bedrock": False,
        "redshift": False,
        "s3": False
    }
    
    # Check Bedrock
    try:
        bedrock_client = aws_auth.get_bedrock_client()
        if bedrock_client:
            checks["bedrock"] = True
    except:
        pass
    
    # Check Redshift
    try:
        redshift_client = aws_auth.get_redshift_client()
        if redshift_client:
            checks["redshift"] = True
    except:
        pass
    
    # Check S3
    try:
        s3_client = aws_auth.get_s3_client()
        if s3_client:
            checks["s3"] = True
    except:
        pass
    
    all_ready = all(checks.values())
    
    return {
        "ready": all_ready,
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check() -> Dict[str, str]:
    """
    Liveness check - simple ping
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }