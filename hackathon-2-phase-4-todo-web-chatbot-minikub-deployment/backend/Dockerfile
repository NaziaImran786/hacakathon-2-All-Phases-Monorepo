# Multi-stage Dockerfile for FastAPI Backend
# Optimized for production deployment with MCP and SQLModel support
# Target image size: < 500MB

# =============================================================================
# Stage 1: Builder - Install dependencies
# =============================================================================
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app
ENV PYTHONPATH=/app

# Install build dependencies for psycopg2-binary and other C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies to user site-packages for easy copying
RUN pip install --no-cache-dir --user -r requirements.txt

# =============================================================================
# Stage 2: Runtime - Minimal production image
# =============================================================================
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only (PostgreSQL client libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy installed dependencies from builder stage
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Copy application code
COPY --chown=appuser:appuser . .

# Ensure Python can find user-installed packages
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Switch to non-root user
USER appuser

# Expose FastAPI port
EXPOSE 8000


# Run uvicorn server
# - 0.0.0.0 allows external connections (required for Kubernetes)
# - Port 8000 is standard for FastAPI
# - app:app refers to app.py:app (the FastAPI instance)
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]



