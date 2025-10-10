# ==================================================
# Dockerfile for Webconnex Text-to-SQL Frontend
# Streamlit UI powered by Amazon Nova Pro
# ==================================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy requirements for frontend
COPY frontend/requirements-frontend.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-frontend.txt

# Copy frontend code and backend dependencies (needed for imports)
COPY --chown=appuser:appuser . .

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Streamlit configuration
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_THEME_PRIMARY_COLOR="#0047AB" \
    STREAMLIT_THEME_BACKGROUND_COLOR="#FFFFFF" \
    STREAMLIT_THEME_SECONDARY_BACKGROUND_COLOR="#F5F7FA"

# Backend API endpoint (can be overridden)
ENV BACKEND_API_URL=http://backend:8000

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "frontend_streamlit_v2.py", \
     "--server.port", "8501", \
     "--server.address", "0.0.0.0", \
     "--server.headless", "true", \
     "--browser.gatherUsageStats", "false"]
