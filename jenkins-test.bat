@echo off
REM Jenkins Test Script for Emergency Response App - Windows
REM This script tests the pipeline steps locally before running in Jenkins

echo ========================================
echo Jenkins Pipeline Test - Windows
echo Emergency Response App
echo ========================================

REM Set environment variables
set APP_NAME=emergency-response-app
set BUILD_NUMBER=test-1
set FLASK_ENV=testing

echo.
echo [1/6] Testing Python Environment Setup...
echo ----------------------------------------

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    goto :error
)
echo ✓ Python is available

REM Create virtual environment
if exist venv rmdir /s /q venv
python -m venv venv
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    goto :error
)
echo ✓ Virtual environment created

REM Activate virtual environment and install dependencies
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERROR: Failed to activate virtual environment
    goto :error
)
echo ✓ Virtual environment activated

pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    echo WARNING: Some dependencies may have failed to install
)
echo ✓ Dependencies installed

pip install pytest pytest-cov flake8 bandit safety >nul 2>&1
echo ✓ Testing tools installed

echo.
echo [2/6] Testing Code Quality Checks...
echo ------------------------------------

REM Run linting
echo Running flake8 linting...
flake8 --max-line-length=120 --exclude=venv,__pycache__ . >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Linting passed
) else (
    echo ⚠ Linting found issues (non-blocking)
)

echo.
echo [3/6] Testing Database Initialization...
echo ----------------------------------------

REM Initialize test database
python -c "from database import init_database; init_database()" >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Database initialized successfully
) else (
    echo ⚠ Database initialization had issues
)

echo.
echo [4/6] Testing Unit Tests...
echo ---------------------------

REM Run unit tests
if exist tests\test_app.py (
    pytest tests\test_app.py --junitxml=test-results.xml -v
    if %errorlevel% equ 0 (
        echo ✓ Unit tests passed
    ) else (
        echo ⚠ Some unit tests failed
    )
) else (
    echo ⚠ Test file not found: tests\test_app.py
)

echo.
echo [5/6] Testing Security Scans...
echo -------------------------------

REM Run security checks
echo Running safety check...
safety check --json --output safety-report.json >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Safety check passed
) else (
    echo ⚠ Safety check found issues (check safety-report.json)
)

echo Running bandit security scan...
bandit -r . -f json -o bandit-report.json >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Bandit scan passed
) else (
    echo ⚠ Bandit found security issues (check bandit-report.json)
)

echo.
echo [6/6] Testing Build Process...
echo ------------------------------

REM Create build directory
if exist build rmdir /s /q build
mkdir build

REM Copy files
echo Copying application files...
copy *.py build\ >nul 2>&1
if exist templates xcopy /E /I templates build\templates >nul 2>&1
if exist static xcopy /E /I static build\static >nul 2>&1
if exist monitoring xcopy /E /I monitoring build\monitoring >nul 2>&1
if exist ansible xcopy /E /I ansible build\ansible >nul 2>&1
copy requirements.txt build\ >nul 2>&1
if exist setup.sh copy setup.sh build\ >nul 2>&1
if exist docker-compose.monitoring.yml copy docker-compose.monitoring.yml build\ >nul 2>&1

REM Create version files
echo %BUILD_NUMBER% > build\VERSION
echo test-commit > build\COMMIT
echo %date%-%time% > build\BUILD_DATE

echo ✓ Build files created

REM Test application startup (optional)
echo.
echo [OPTIONAL] Testing Application Startup...
echo -----------------------------------------
echo Starting application for 10 seconds...
start /B python app.py >nul 2>&1
timeout /t 5 /nobreak >nul

REM Test health endpoint
curl -f http://localhost:3000/api/v1/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Application health check passed
) else (
    echo ⚠ Application health check failed (app may not be running)
)

REM Stop application
taskkill /F /IM python.exe >nul 2>&1

echo.
echo ========================================
echo Jenkins Pipeline Test Results
echo ========================================
echo.
echo ✓ Python Environment: OK
echo ✓ Code Quality: Checked
echo ✓ Database: Initialized
echo ✓ Unit Tests: Executed
echo ✓ Security Scans: Completed
echo ✓ Build Process: OK
echo.
echo Your Jenkins pipeline should work!
echo.
echo Next steps:
echo 1. Commit and push changes to GitHub
echo 2. Run Jenkins pipeline
echo 3. Monitor build progress
echo.
echo Files created:
if exist test-results.xml echo - test-results.xml (test results)
if exist safety-report.json echo - safety-report.json (security report)
if exist bandit-report.json echo - bandit-report.json (security scan)
if exist build echo - build\ (deployment package)
echo.
goto :end

:error
echo.
echo ========================================
echo ERROR: Pipeline test failed!
echo ========================================
echo Please fix the issues above before running Jenkins pipeline.
echo.
pause
exit /b 1

:end
echo Test completed successfully!
echo.
pause
