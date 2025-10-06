# =============================================================================
# Multi-stage Dockerfile for Economic Dashboard API
# Optimized for production deployment on Railway
# =============================================================================

# -----------------------------------------------------------------------------
# Stage 1: Builder - Install dependencies
# -----------------------------------------------------------------------------
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file from backend directory
COPY backend/requirements.txt .

# Install Python dependencies in a virtual environment
# This allows us to copy only the venv to the final stage
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# -----------------------------------------------------------------------------
# Stage 2: Runtime - Create minimal production image
# -----------------------------------------------------------------------------
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install only runtime dependencies (PostgreSQL client for health checks)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv

# Copy application code from backend directory
COPY backend/ .

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port 8000
EXPOSE 8000

# Health check using curl (more reliable than Python import in container)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health/liveness || exit 1

# Default command: Run migrations then start server
# Railway will use the startCommand from railway.json
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4"]

# Alternative command for development (commented out):
# CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Alternative command with Gunicorn (uncomment if preferred):
# CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--timeout", "120"]
