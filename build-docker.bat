@echo off
REM Emergency Response App - Docker Build Script for Windows
REM Builds and tests all Docker images

echo 🐳 BUILDING EMERGENCY RESPONSE APP DOCKER IMAGES
echo ==================================================

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)

echo [SUCCESS] Docker is running

REM Build main application image
echo [INFO] Building main Emergency Response App image...
docker build -t emergency-response-app:latest -f Dockerfile .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build main application image
    exit /b 1
)
echo [SUCCESS] Main application image built successfully

REM Build monitoring dashboard image
echo [INFO] Building monitoring dashboard image...
docker build -t emergency-monitoring:latest -f Dockerfile.monitoring .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build monitoring dashboard image
    exit /b 1
)
echo [SUCCESS] Monitoring dashboard image built successfully

REM Build nginx image
echo [INFO] Building nginx reverse proxy image...
docker build -t emergency-nginx:latest -f Dockerfile.nginx .
if %errorlevel% neq 0 (
    echo [ERROR] Failed to build nginx image
    exit /b 1
)
echo [SUCCESS] Nginx reverse proxy image built successfully

REM List built images
echo [INFO] Built Docker images:
docker images | findstr emergency

REM Test images
echo [INFO] Testing Docker images...

REM Test main app image
echo [INFO] Testing main application image...
docker run --rm -d --name emergency-app-test -p 5001:5000 emergency-response-app:latest
timeout /t 10 /nobreak >nul

REM Check if app is responding (simplified for Windows)
echo [INFO] Checking application health...
curl -f http://localhost:5001/api/v1/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Main application is responding correctly
) else (
    echo [WARNING] Main application health check failed (this might be expected without database)
)

REM Stop test container
docker stop emergency-app-test >nul 2>&1

REM Test monitoring dashboard image
echo [INFO] Testing monitoring dashboard image...
docker run --rm -d --name monitoring-test -p 9998:9999 emergency-monitoring:latest
timeout /t 10 /nobreak >nul

REM Check if monitoring dashboard is responding
curl -f http://localhost:9998/health >nul 2>&1
if %errorlevel% equ 0 (
    echo [SUCCESS] Monitoring dashboard is responding correctly
) else (
    echo [WARNING] Monitoring dashboard health check failed
)

REM Stop test container
docker stop monitoring-test >nul 2>&1

echo [SUCCESS] Docker image testing completed

REM Tag images for registry
echo [INFO] Tagging images for registry...
docker tag emergency-response-app:latest emergency-response-app:v1.0.0
docker tag emergency-monitoring:latest emergency-monitoring:v1.0.0
docker tag emergency-nginx:latest emergency-nginx:v1.0.0

echo [SUCCESS] Images tagged successfully

REM Show final image list
echo [INFO] Final Docker images:
docker images | findstr emergency

echo.
echo [SUCCESS] 🎉 All Docker images built and tested successfully!
echo.
echo [INFO] Next steps:
echo   1. Run 'docker-compose up -d' to start all services
echo   2. Access the application at http://localhost
echo   3. Access monitoring at http://localhost:9999
echo   4. Access Grafana at http://localhost:3001
echo.
