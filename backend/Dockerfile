# Production-ready multi-stage Dockerfile for Elogia v4 Backend
# Uses Python 3.12-slim with asyncpg dependencies for PostgreSQL

# ---- Base stage for building dependencies ----
FROM python:3.12-slim AS builder

# Install system dependencies required for asyncpg and PostgreSQL client
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ---- Production stage ----
FROM python:3.12-slim

# Install runtime dependencies for asyncpg (libpq only, no build tools)
RUN apt-get update && apt-get install -y \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app
USER appuser

# Set working directory
WORKDIR /app

# Copy application code
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./migrations ./migrations
COPY --chown=appuser:appuser ./storage ./storage
COPY --chown=appuser:appuser ./requirements.txt .
COPY --chown=appuser:appuser ./Makefile .
COPY --chown=appuser:appuser ./.env.example .
COPY --chown=appuser:appuser ./alembic.ini .

# Environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV DATABASE_URL="postgresql+asyncpg://elogia_user:elogia_password@postgres:5432/elogia_db"

# Expose FastAPI port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/status || exit 1

# Run database migrations and start FastAPI server
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
