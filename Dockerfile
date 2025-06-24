# Emergency Response App - Production Dockerfile
FROM python:3.12-slim

# Set metadata
LABEL maintainer="Emergency Response Team"
LABEL description="Emergency Response App for Cameroon"
LABEL version="1.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    wget \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r emergency && useradd -r -g emergency emergency

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Initialize database if it doesn't exist
RUN python -c "from database import init_database; init_database()" || true

# Set proper permissions
RUN chown -R emergency:emergency /app

# Switch to non-root user
USER emergency

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:3000/api/v1/health', timeout=5).raise_for_status()" || exit 1

# Start application
CMD ["python", "app.py"]
