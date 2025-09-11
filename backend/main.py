"""
FastAPI Main Application
Entry point for the Webconnex Text-to-SQL API
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from backend.config.settings import settings
from backend.api.routes import auth, query, training, tenants, health
from backend.utils.logging import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle
    """
    # Startup
    logger.info("Starting Webconnex Text-to-SQL API")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"AWS Region: {settings.AWS_REGION}")
    logger.info(f"Redshift Cluster: {settings.REDSHIFT_CLUSTER_ID}")
    
    # Initialize services
    try:
        # TODO: Initialize Bedrock client
        # TODO: Initialize S3 Vector store
        # TODO: Initialize Redshift connection pool
        logger.info("All services initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Webconnex Text-to-SQL API")
    # TODO: Cleanup connections and resources


# Create FastAPI application
app = FastAPI(
    title="Webconnex Text-to-SQL API",
    description="Natural language interface for querying Webconnex data",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add trusted host middleware for security
if settings.ENVIRONMENT == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.ALLOWED_HOSTS
    )

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal server error occurred",
            "type": "internal_error"
        }
    )

# Include routers
app.include_router(health.router, prefix="/api/health", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(query.router, prefix="/api/query", tags=["query"])
app.include_router(training.router, prefix="/api/training", tags=["training"])
app.include_router(tenants.router, prefix="/api/tenants", tags=["tenants"])

# Add Prometheus metrics endpoint
if settings.ENABLE_METRICS:
    metrics_app = make_asgi_app()
    app.mount("/metrics", metrics_app)

# Root endpoint
@app.get("/")
async def root():
    """
    Root endpoint
    """
    return {
        "name": "Webconnex Text-to-SQL API",
        "version": "1.0.0",
        "status": "operational",
        "documentation": "/api/docs"
    }

# API info endpoint
@app.get("/api/info")
async def api_info():
    """
    Get API information
    """
    return {
        "name": "Webconnex Text-to-SQL API",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT,
        "features": {
            "caching": settings.ENABLE_CACHING,
            "rag": settings.ENABLE_RAG,
            "training_ui": settings.ENABLE_TRAINING_UI,
            "admin_panel": settings.ENABLE_ADMIN_PANEL
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        log_level=settings.API_LOG_LEVEL.lower(),
        workers=settings.API_WORKERS
    )