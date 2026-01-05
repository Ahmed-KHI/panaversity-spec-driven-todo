# Dockerfile for Hugging Face Spaces
# This file is optimized for HF Spaces deployment

FROM python:3.13-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=7860

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY src/ ./src/

# Expose port 7860 (required by Hugging Face Spaces)
EXPOSE 7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:7860/health')"

# Run the application
# Note: --host 0.0.0.0 to accept connections from outside container
# Note: --port 7860 is required by Hugging Face Spaces
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "1"]
