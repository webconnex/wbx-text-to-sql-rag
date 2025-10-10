"""
Application Settings
Central configuration management using Pydantic
"""

import os
from typing import List, Optional
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with validation
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"  # Ignore extra fields in .env
    )
    
    # Environment
    ENVIRONMENT: str = Field(default="development", description="Environment name")
    DEBUG: bool = Field(default=False, description="Debug mode")
    TESTING: bool = Field(default=False, description="Testing mode")
    
    # AWS Configuration - New Account (webconnex-ai-dev)
    AWS_REGION: str = Field(default="us-west-2", description="AWS region")
    AWS_ACCOUNT_ID: str = Field(default="049101138630", description="AWS account ID - webconnex-ai-dev")
    AWS_PROFILE: Optional[str] = Field(default="049101138630-okta-admin-user", description="AWS profile")
    
    # Redshift Configuration
    REDSHIFT_CLUSTER_ID: str = Field(default="wbx-data", description="Redshift cluster ID")
    REDSHIFT_DATABASE: str = Field(default="wbx_data", description="Redshift database")
    REDSHIFT_SCHEMA: str = Field(default="public", description="Redshift schema")
    REDSHIFT_SECRET_ARN: str = Field(default="wbx-data/db/replicator", description="Redshift secret ARN")
    REDSHIFT_WORKGROUP: str = Field(default="default", description="Redshift workgroup")
    
    # AWS Bedrock Configuration
    BEDROCK_MODEL_ID: str = Field(
        default="us.amazon.nova-pro-v1:0",
        description="Bedrock model ID for text generation"
    )
    BEDROCK_MODEL_ID_EMBEDDINGS: str = Field(
        default="amazon.titan-embed-text-v2:0",
        description="Bedrock model ID for embeddings - Titan V2"
    )
    BEDROCK_REGION: str = Field(default="us-west-2", description="Bedrock region")
    BEDROCK_MAX_TOKENS: int = Field(default=1000, description="Max tokens for Bedrock")
    
    # S3 Configuration - New Account Buckets
    S3_BUCKET_VECTORS: str = Field(
        default="webconnex-ai-dev-vectors",
        description="S3 bucket for vectors (new account)"
    )
    S3_BUCKET_TRAINING: str = Field(
        default="webconnex-ai-dev-training",
        description="S3 bucket for training data (new account)"
    )
    S3_REGION: str = Field(default="us-west-2", description="S3 region")
    
    # Authentication
    OKTA_DOMAIN: str = Field(default="", description="Okta domain")
    OKTA_CLIENT_ID: str = Field(default="", description="Okta client ID")
    OKTA_CLIENT_SECRET: str = Field(default="", description="Okta client secret")
    OKTA_REDIRECT_URI: str = Field(
        default="http://localhost:3000/callback",
        description="Okta redirect URI"
    )
    JWT_SECRET_KEY: str = Field(
        default="change-this-secret-key-in-production",
        description="JWT secret key"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    JWT_EXPIRATION_MINUTES: int = Field(default=60, description="JWT expiration in minutes")
    
    # API Configuration
    API_HOST: str = Field(default="0.0.0.0", description="API host")
    API_PORT: int = Field(default=8000, description="API port")
    API_WORKERS: int = Field(default=4, description="Number of API workers")
    API_RELOAD: bool = Field(default=True, description="Enable auto-reload")
    API_LOG_LEVEL: str = Field(default="INFO", description="API log level")
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000"],
        description="CORS allowed origins"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["*"],
        description="Allowed hosts for production"
    )
    
    # Database Connection Pool
    DB_POOL_SIZE: int = Field(default=20, description="Database pool size")
    DB_MAX_OVERFLOW: int = Field(default=10, description="Max overflow connections")
    DB_POOL_TIMEOUT: int = Field(default=30, description="Pool timeout in seconds")
    DB_POOL_RECYCLE: int = Field(default=3600, description="Connection recycle time")
    
    # Query Limits
    MAX_QUERY_RESULTS: int = Field(default=10000, description="Max query results")
    QUERY_TIMEOUT_SECONDS: int = Field(default=300, description="Query timeout")
    MAX_CONCURRENT_QUERIES: int = Field(default=10, description="Max concurrent queries")
    
    # Cache Configuration
    REDIS_HOST: str = Field(default="localhost", description="Redis host")
    REDIS_PORT: int = Field(default=6379, description="Redis port")
    REDIS_DB: int = Field(default=0, description="Redis database")
    CACHE_TTL_SECONDS: int = Field(default=3600, description="Cache TTL in seconds")
    
    # Monitoring
    ENABLE_METRICS: bool = Field(default=True, description="Enable metrics")
    METRICS_PORT: int = Field(default=9090, description="Metrics port")
    CLOUDWATCH_NAMESPACE: str = Field(
        default="WebconnexTextToSQL",
        description="CloudWatch namespace"
    )
    CLOUDWATCH_REGION: str = Field(default="us-west-2", description="CloudWatch region")
    
    # Feature Flags
    ENABLE_CACHING: bool = Field(default=True, description="Enable caching")
    ENABLE_RAG: bool = Field(default=True, description="Enable RAG")
    ENABLE_TRAINING_UI: bool = Field(default=False, description="Enable training UI")
    ENABLE_ADMIN_PANEL: bool = Field(default=False, description="Enable admin panel")
    
    # Development
    RUN_LOCALLY: bool = Field(default=True, description="Run locally flag")
    
    # Logging
    LOG_FORMAT: str = Field(default="json", description="Log format")
    LOG_FILE_PATH: str = Field(default="logs/app.log", description="Log file path")
    LOG_MAX_SIZE: str = Field(default="100M", description="Max log file size")
    LOG_BACKUP_COUNT: int = Field(default=5, description="Log backup count")
    
    # Security
    ENABLE_RATE_LIMITING: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Rate limit requests")
    RATE_LIMIT_PERIOD: int = Field(default=60, description="Rate limit period in seconds")
    ENABLE_QUERY_VALIDATION: bool = Field(default=True, description="Enable query validation")
    ENABLE_SQL_INJECTION_PROTECTION: bool = Field(
        default=True,
        description="Enable SQL injection protection"
    )
    
    # Vanna AI Configuration
    VANNA_API_KEY: Optional[str] = Field(default=None, description="Vanna API key")
    VANNA_MODEL_NAME: str = Field(
        default="webconnex-text-to-sql",
        description="Vanna model name"
    )
    VANNA_ALLOW_LLM_SEE_DATA: bool = Field(
        default=False,
        description="Allow LLM to see data"
    )
    
    # gimme-aws-creds Configuration - New Account
    GIMME_AWS_CREDS_PROFILE: str = Field(
        default="049101138630-okta-admin-user",
        description="gimme-aws-creds profile for new account"
    )
    GIMME_AWS_CREDS_DURATION: int = Field(
        default=3600,
        description="Credential duration"
    )
    
    @property
    def redis_url(self) -> str:
        """Get Redis connection URL"""
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production"""
        return self.ENVIRONMENT.lower() == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development"""
        return self.ENVIRONMENT.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance
    """
    return Settings()


# Create settings instance
settings = get_settings()