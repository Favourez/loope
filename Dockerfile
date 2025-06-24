# Emergency Response App - Production Dockerfile
FROM python:3.11-alpine

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

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/data

# Create non-root user
RUN addgroup -g 1001 -S emergency && \
    adduser -S emergency -G emergency

# Set proper permissions
RUN chown -R emergency:emergency /app

# Switch to non-root user
USER emergency

# Expose port
EXPOSE 3000

# Run the application
CMD ["python", "app.py"]
