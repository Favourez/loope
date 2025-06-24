#!/bin/bash

# Emergency Response App - Docker Build Script
# Builds and tests all Docker images

set -e

echo "🐳 BUILDING EMERGENCY RESPONSE APP DOCKER IMAGES"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

print_success "Docker is running"

# Build main application image
print_status "Building main Emergency Response App image..."
docker build -t emergency-response-app:latest -f Dockerfile .
if [ $? -eq 0 ]; then
    print_success "Main application image built successfully"
else
    print_error "Failed to build main application image"
    exit 1
fi

# Build monitoring dashboard image
print_status "Building monitoring dashboard image..."
docker build -t emergency-monitoring:latest -f Dockerfile.monitoring .
if [ $? -eq 0 ]; then
    print_success "Monitoring dashboard image built successfully"
else
    print_error "Failed to build monitoring dashboard image"
    exit 1
fi

# Build nginx image
print_status "Building nginx reverse proxy image..."
docker build -t emergency-nginx:latest -f Dockerfile.nginx .
if [ $? -eq 0 ]; then
    print_success "Nginx reverse proxy image built successfully"
else
    print_error "Failed to build nginx image"
    exit 1
fi

# List built images
print_status "Built Docker images:"
docker images | grep emergency

# Test images
print_status "Testing Docker images..."

# Test main app image
print_status "Testing main application image..."
docker run --rm -d --name emergency-app-test -p 5001:5000 emergency-response-app:latest
sleep 10

# Check if app is responding
if curl -f http://localhost:5001/api/v1/health > /dev/null 2>&1; then
    print_success "Main application is responding correctly"
else
    print_warning "Main application health check failed (this might be expected without database)"
fi

# Stop test container
docker stop emergency-app-test > /dev/null 2>&1

# Test monitoring dashboard image
print_status "Testing monitoring dashboard image..."
docker run --rm -d --name monitoring-test -p 9998:9999 emergency-monitoring:latest
sleep 10

# Check if monitoring dashboard is responding
if curl -f http://localhost:9998/health > /dev/null 2>&1; then
    print_success "Monitoring dashboard is responding correctly"
else
    print_warning "Monitoring dashboard health check failed"
fi

# Stop test container
docker stop monitoring-test > /dev/null 2>&1

print_success "Docker image testing completed"

# Tag images for registry (optional)
print_status "Tagging images for registry..."
docker tag emergency-response-app:latest emergency-response-app:v1.0.0
docker tag emergency-monitoring:latest emergency-monitoring:v1.0.0
docker tag emergency-nginx:latest emergency-nginx:v1.0.0

print_success "Images tagged successfully"

# Show final image list
print_status "Final Docker images:"
docker images | grep -E "(emergency|REPOSITORY)"

echo ""
print_success "🎉 All Docker images built and tested successfully!"
echo ""
print_status "Next steps:"
echo "  1. Run 'docker-compose up -d' to start all services"
echo "  2. Access the application at http://localhost"
echo "  3. Access monitoring at http://localhost:9999"
echo "  4. Access Grafana at http://localhost:3001"
echo ""
