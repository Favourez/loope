@echo off
REM Automated test execution script for Emergency Response App (Windows)
REM Runs comprehensive test suite with coverage analysis

echo ========================================
echo Emergency Response App - Test Suite
echo ========================================

REM Set environment variables
set PYTHONPATH=%CD%
set FLASK_ENV=testing

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Parse command line arguments
set RUN_UNIT=0
set RUN_INTEGRATION=0
set RUN_E2E=0
set RUN_PERFORMANCE=0
set RUN_SECURITY=0
set RUN_COVERAGE=0
set RUN_SETUP=0
set RUN_FAST=0
set RUN_ALL=1

:parse_args
if "%1"=="--unit" (
    set RUN_UNIT=1
    set RUN_ALL=0
    shift
    goto parse_args
)
if "%1"=="--integration" (
    set RUN_INTEGRATION=1
    set RUN_ALL=0
    shift
    goto parse_args
)
if "%1"=="--e2e" (
    set RUN_E2E=1
    set RUN_ALL=0
    shift
    goto parse_args
)
if "%1"=="--performance" (
    set RUN_PERFORMANCE=1
    set RUN_ALL=0
    shift
    goto parse_args
)
if "%1"=="--security" (
    set RUN_SECURITY=1
    set RUN_ALL=0
    shift
    goto parse_args
)
if "%1"=="--coverage" (
    set RUN_COVERAGE=1
    set RUN_ALL=0
    shift
    goto parse_args
)
if "%1"=="--setup" (
    set RUN_SETUP=1
    set RUN_ALL=0
    shift
    goto parse_args
)
if "%1"=="--fast" (
    set RUN_FAST=1
    set RUN_ALL=0
    shift
    goto parse_args
)
if "%1"=="--help" (
    goto show_help
)
if not "%1"=="" (
    shift
    goto parse_args
)

REM Show help if requested
if "%1"=="--help" goto show_help

echo.
echo Starting test execution...
echo Time: %date% %time%
echo.

REM Create necessary directories
if not exist htmlcov mkdir htmlcov
if not exist test-reports mkdir test-reports
if not exist logs mkdir logs

REM Setup test environment
echo [1/7] Setting up test environment...
echo ----------------------------------------

REM Install test dependencies
echo Installing test dependencies...
pip install pytest>=7.0.0 pytest-cov>=4.0.0 pytest-html>=3.0.0 >nul 2>&1
pip install pytest-xdist>=3.0.0 pytest-timeout>=2.0.0 >nul 2>&1
pip install selenium>=4.0.0 coverage>=7.0.0 >nul 2>&1
pip install bandit safety >nul 2>&1

if %errorlevel% neq 0 (
    echo WARNING: Some test dependencies may not have installed correctly
)

echo Test environment setup completed.

REM Run tests based on arguments
if %RUN_SETUP%==1 (
    echo Setup completed.
    goto end
)

if %RUN_UNIT%==1 goto run_unit_tests
if %RUN_INTEGRATION%==1 goto run_integration_tests
if %RUN_E2E%==1 goto run_e2e_tests
if %RUN_PERFORMANCE%==1 goto run_performance_tests
if %RUN_SECURITY%==1 goto run_security_tests
if %RUN_COVERAGE%==1 goto run_coverage_only
if %RUN_FAST%==1 goto run_fast_tests
if %RUN_ALL%==1 goto run_all_tests

goto run_all_tests

:run_unit_tests
echo.
echo [2/7] Running Unit Tests...
echo ----------------------------------------
python -m pytest tests/test_app.py tests/test_database.py tests/test_auth.py --verbose --tb=short --cov=. --cov-report=html:htmlcov --cov-report=xml:coverage.xml --junitxml=test-reports/unit-tests.xml
if %errorlevel% equ 0 (
    echo Unit tests: PASSED
) else (
    echo Unit tests: FAILED
)
goto end

:run_integration_tests
echo.
echo [3/7] Running Integration Tests...
echo ----------------------------------------
if exist tests\test_integration.py (
    python -m pytest tests/test_integration.py --verbose --tb=short --junitxml=test-reports/integration-tests.xml
    if %errorlevel% equ 0 (
        echo Integration tests: PASSED
    ) else (
        echo Integration tests: FAILED
    )
) else (
    echo Integration test file not found
)
goto end

:run_e2e_tests
echo.
echo [4/7] Running End-to-End Tests...
echo ----------------------------------------
if exist tests\test_e2e.py (
    python -m pytest tests/test_e2e.py --verbose --tb=short --junitxml=test-reports/e2e-tests.xml
    if %errorlevel% equ 0 (
        echo E2E tests: PASSED
    ) else (
        echo E2E tests: FAILED
    )
) else (
    echo E2E test file not found
)
goto end

:run_performance_tests
echo.
echo [5/7] Running Performance Tests...
echo ----------------------------------------
python -m pytest --verbose --tb=short -k "performance or Performance" --junitxml=test-reports/performance-tests.xml
if %errorlevel% equ 0 (
    echo Performance tests: PASSED
) else (
    echo Performance tests: WARNING (non-critical)
)
goto end

:run_security_tests
echo.
echo [6/7] Running Security Tests...
echo ----------------------------------------

REM Run bandit security analysis
echo Running Bandit security analysis...
bandit -r . -f json -o test-reports/bandit-report.json >nul 2>&1
if %errorlevel% equ 0 (
    echo Bandit scan: PASSED
) else (
    echo Bandit scan: WARNING
)

REM Run safety check
echo Running Safety dependency check...
safety check --json --output test-reports/safety-report.json >nul 2>&1
if %errorlevel% equ 0 (
    echo Safety check: PASSED
) else (
    echo Safety check: WARNING
)

REM Run auth tests
if exist tests\test_auth.py (
    python -m pytest tests/test_auth.py --verbose --tb=short
    if %errorlevel% equ 0 (
        echo Auth tests: PASSED
    ) else (
        echo Auth tests: FAILED
    )
)
goto end

:run_coverage_only
echo.
echo [7/7] Generating Coverage Report...
echo ----------------------------------------
if exist tests\test_coverage_analysis.py (
    python tests/test_coverage_analysis.py
) else (
    echo Coverage analysis script not found
)
goto end

:run_fast_tests
echo.
echo Running Fast Test Suite (excluding E2E)...
echo ========================================

call :run_unit_tests_internal
call :run_integration_tests_internal
call :run_performance_tests_internal
call :run_security_tests_internal
call :run_coverage_internal

goto summary

:run_all_tests
echo.
echo Running Complete Test Suite...
echo ========================================

call :run_unit_tests_internal
call :run_integration_tests_internal
call :run_e2e_tests_internal
call :run_performance_tests_internal
call :run_security_tests_internal
call :run_coverage_internal

goto summary

REM Internal test functions
:run_unit_tests_internal
echo.
echo [2/7] Running Unit Tests...
echo ----------------------------------------
python -m pytest tests/test_app.py tests/test_database.py tests/test_auth.py --verbose --tb=short --cov=. --cov-report=html:htmlcov --cov-report=xml:coverage.xml --junitxml=test-reports/unit-tests.xml
if %errorlevel% equ 0 (
    echo Unit tests: PASSED
    set UNIT_RESULT=PASSED
) else (
    echo Unit tests: FAILED
    set UNIT_RESULT=FAILED
)
goto :eof

:run_integration_tests_internal
echo.
echo [3/7] Running Integration Tests...
echo ----------------------------------------
if exist tests\test_integration.py (
    python -m pytest tests/test_integration.py --verbose --tb=short --junitxml=test-reports/integration-tests.xml
    if %errorlevel% equ 0 (
        echo Integration tests: PASSED
        set INTEGRATION_RESULT=PASSED
    ) else (
        echo Integration tests: FAILED
        set INTEGRATION_RESULT=FAILED
    )
) else (
    echo Integration test file not found
    set INTEGRATION_RESULT=SKIPPED
)
goto :eof

:run_e2e_tests_internal
echo.
echo [4/7] Running End-to-End Tests...
echo ----------------------------------------
if exist tests\test_e2e.py (
    python -m pytest tests/test_e2e.py --verbose --tb=short --junitxml=test-reports/e2e-tests.xml
    if %errorlevel% equ 0 (
        echo E2E tests: PASSED
        set E2E_RESULT=PASSED
    ) else (
        echo E2E tests: FAILED
        set E2E_RESULT=FAILED
    )
) else (
    echo E2E test file not found
    set E2E_RESULT=SKIPPED
)
goto :eof

:run_performance_tests_internal
echo.
echo [5/7] Running Performance Tests...
echo ----------------------------------------
python -m pytest --verbose --tb=short -k "performance or Performance" --junitxml=test-reports/performance-tests.xml
if %errorlevel% equ 0 (
    echo Performance tests: PASSED
    set PERFORMANCE_RESULT=PASSED
) else (
    echo Performance tests: WARNING
    set PERFORMANCE_RESULT=WARNING
)
goto :eof

:run_security_tests_internal
echo.
echo [6/7] Running Security Tests...
echo ----------------------------------------
bandit -r . -f json -o test-reports/bandit-report.json >nul 2>&1
safety check --json --output test-reports/safety-report.json >nul 2>&1
if exist tests\test_auth.py (
    python -m pytest tests/test_auth.py --verbose --tb=short
    if %errorlevel% equ 0 (
        echo Security tests: PASSED
        set SECURITY_RESULT=PASSED
    ) else (
        echo Security tests: WARNING
        set SECURITY_RESULT=WARNING
    )
) else (
    set SECURITY_RESULT=SKIPPED
)
goto :eof

:run_coverage_internal
echo.
echo [7/7] Generating Coverage Report...
echo ----------------------------------------
if exist tests\test_coverage_analysis.py (
    python tests/test_coverage_analysis.py
    set COVERAGE_RESULT=COMPLETED
) else (
    echo Coverage analysis script not found
    set COVERAGE_RESULT=SKIPPED
)
goto :eof

:summary
echo.
echo ========================================
echo TEST EXECUTION SUMMARY
echo ========================================
echo Unit Tests:        %UNIT_RESULT%
echo Integration Tests: %INTEGRATION_RESULT%
echo E2E Tests:         %E2E_RESULT%
echo Performance Tests: %PERFORMANCE_RESULT%
echo Security Tests:    %SECURITY_RESULT%
echo Coverage Report:   %COVERAGE_RESULT%
echo ----------------------------------------
echo Completed at: %date% %time%
echo.
echo Generated Reports:
echo - HTML Coverage: htmlcov\index.html
echo - XML Coverage: coverage.xml
echo - Test Results: test-reports\
echo ========================================

goto end

:show_help
echo.
echo Emergency Response App Test Suite
echo.
echo Usage: run_tests.bat [options]
echo.
echo Options:
echo   --unit         Run only unit tests
echo   --integration  Run only integration tests
echo   --e2e          Run only end-to-end tests
echo   --performance  Run only performance tests
echo   --security     Run only security tests
echo   --coverage     Generate coverage report only
echo   --setup        Setup test environment only
echo   --fast         Run fast tests (exclude E2E)
echo   --help         Show this help message
echo.
echo Examples:
echo   run_tests.bat                 # Run all tests
echo   run_tests.bat --unit          # Run only unit tests
echo   run_tests.bat --fast          # Run all except E2E tests
echo   run_tests.bat --coverage      # Generate coverage report only
echo.
goto end

:end
echo.
pause
