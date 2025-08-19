# Multi-stage Docker build for ISS Data Analytics System - Ingestion Service
# Optimized for monorepo structure with shared libraries

# Build stage - Install dependencies and build workspace
FROM python:3.11-slim AS builder

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast Python package management (latest version with workspace support)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh && \
    mv ~/.local/bin/uv /usr/local/bin/uv

# Set working directory to repository root for monorepo access
WORKDIR /app

# Copy workspace configuration files first for better Docker layer caching
COPY pyproject.toml uv.lock ./

# Copy shared libraries and service-specific files
COPY libs/ libs/
COPY services/ingestion/ services/ingestion/

# Install all workspace dependencies including shared libraries
RUN uv sync --frozen --no-dev --workspace

# Production stage - Minimal runtime image
FROM python:3.11-slim AS runtime

# Create non-root user for security
RUN groupadd --gid 1001 --system appgroup && \
    useradd --uid 1001 --system --gid appgroup --home-dir /app --shell /bin/bash appuser

# Install minimal runtime dependencies including curl for health checks
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set working directory
WORKDIR /app

# Copy virtual environment from builder stage
COPY --from=builder --chown=appuser:appgroup /app/.venv /app/.venv

# Copy application code and shared libraries
COPY --from=builder --chown=appuser:appgroup /app/services/ingestion /app/services/ingestion
COPY --from=builder --chown=appuser:appgroup /app/libs /app/libs

# Add virtual environment to PATH
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app"

# Switch to non-root user
USER appuser

# Expose the application port
EXPOSE 8000

# Health check endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Set working directory to service directory for runtime
WORKDIR /app/services/ingestion

# Start the FastAPI application with Uvicorn
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
