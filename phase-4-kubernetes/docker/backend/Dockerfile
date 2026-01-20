# [Task]: T019
# [From]: specs/004-phase-iv-kubernetes/spec.md §REQ-002 (Backend Containerization)
#         specs/004-phase-iv-kubernetes/plan.md §4.1.2 (Backend Dockerfile Design)

# Multi-Stage Build for FastAPI Backend (Production)
# Target Size: < 150MB
# Base: Python 3.12 Alpine
# Features: UV package manager, Uvicorn with 4 workers, non-root user

# ==========================================
# Stage 1: Builder
# ==========================================
FROM python:3.12-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev

WORKDIR /app

# Install UV (fast Python package manager)
RUN pip install --no-cache-dir uv

# Copy dependency files
COPY pyproject.toml requirements.txt* ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Install dependencies with UV (faster than pip)
RUN uv pip install --no-cache -r requirements.txt || pip install --no-cache-dir -r requirements.txt

# ==========================================
# Stage 2: Runner (Production)
# ==========================================
FROM python:3.12-alpine AS runner

# Install runtime dependencies only
RUN apk add --no-cache \
    libpq \
    libffi

WORKDIR /app

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy application source
COPY src ./src
COPY migrations ./migrations

# Create non-root user for security
RUN addgroup --system --gid 1001 fastapi && \
    adduser --system --uid 1001 fastapi && \
    chown -R fastapi:fastapi /app

# Switch to non-root user
USER fastapi

# Expose port 8000
EXPOSE 8000

# Environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH" \
    WORKERS=1

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health').raise_for_status()"

# Start Uvicorn server (workers controlled by WORKERS env var)
CMD uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers ${WORKERS} --log-level info
