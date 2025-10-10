# ==================================================
# Multi-Stage Dockerfile for Webconnex Text-to-SQL Backend
# Optimized for Amazon Nova Pro + AWS Bedrock
# ==================================================

# Stage 1: Build stage with all build dependencies
FROM python:3.11-slim AS builder

# Set working directory
WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    postgresql-client \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt

# ==================================================
# Stage 2: Runtime stage (minimal)
# ==================================================
FROM python:3.11-slim AS runtime

# Install only runtime dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /app/logs /app/data && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# AWS Environment Variables (defaults - override via docker-compose or .env)
ENV AWS_REGION=us-west-2 \
    AWS_ACCOUNT_ID=049101138630 \
    AWS_PROFILE=049101138630-okta-admin-user \
    BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0 \
    BEDROCK_MODEL_ID_EMBEDDINGS=amazon.titan-embed-text-v1 \
    S3_BUCKET_VECTORS=webconnex-ai-dev-vectors \
    S3_BUCKET_TRAINING=webconnex-ai-dev-training \
    REDSHIFT_CLUSTER_ID=wbx-data \
    REDSHIFT_DATABASE=wbx_data \
    REDSHIFT_SCHEMA=webconnex

# Application configuration
ENV ENVIRONMENT=production \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    LOG_LEVEL=INFO

# Switch to non-root user
USER appuser

# Health check with comprehensive validation
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# Expose port
EXPOSE 8000

# Run the application with optimized settings
CMD ["uvicorn", "backend.main:app", \
     "--host", "0.0.0.0", \
     "--port", "8000", \
     "--workers", "4", \
     "--log-level", "info", \
     "--access-log", \
     "--no-access-log"]