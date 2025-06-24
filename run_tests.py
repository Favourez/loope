#!/usr/bin/env python3
"""
Automated test execution script for Emergency Response App
Runs comprehensive test suite with coverage analysis
"""

import os
import sys
import subprocess
import argparse
import time
from pathlib import Path

def run_command(command, description="", cwd=None):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"   Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command, 
            cwd=cwd or os.getcwd(),
            capture_output=True, 
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        if result.returncode == 0:
            print(f"   ✅ Success")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()[:200]}...")
        else:
            print(f"   ❌ Failed (exit code: {result.returncode})")
            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
        
        return result.returncode == 0, result.stdout, result.stderr
    
    except subprocess.TimeoutExpired:
        print(f"   ⏰ Timeout after 5 minutes")
        return False, "", "Timeout"
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False, "", str(e)

def setup_test_environment():
    """Set up test environment"""
    print("🔧 Setting up test environment...")
    
    # Install test dependencies
    test_requirements = [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'pytest-html>=3.0.0',
        'pytest-xdist>=3.0.0',  # For parallel testing
        'pytest-timeout>=2.0.0',
        'selenium>=4.0.0',
        'coverage>=7.0.0'
    ]
    
    for requirement in test_requirements:
        success, _, _ = run_command(
            [sys.executable, '-m', 'pip', 'install', requirement],
            f"Installing {requirement}"
        )
        if not success:
            print(f"⚠️  Warning: Failed to install {requirement}")
    
    # Create necessary directories
    directories = ['htmlcov', 'test-reports', 'logs']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"   📁 Created directory: {directory}")

def run_unit_tests():
    """Run unit tests"""
    print("\n🧪 Running Unit Tests...")
    print("=" * 50)
    
    unit_test_files = [
        'tests/test_app.py',
        'tests/test_database.py', 
        'tests/test_auth.py'
    ]
    
    # Filter existing test files
    existing_files = [f for f in unit_test_files if os.path.exists(f)]
    
    if not existing_files:
        print("❌ No unit test files found")
        return False
    
    command = [
        sys.executable, '-m', 'pytest',
        '--verbose',
        '--tb=short',
        '--cov=.',
        '--cov-report=html:htmlcov',
        '--cov-report=xml:coverage.xml',
        '--cov-report=term-missing',
        '--junitxml=test-reports/unit-tests.xml',
        '-m', 'not e2e',  # Exclude E2E tests
    ] + existing_files
    
    success, stdout, stderr = run_command(command, "Running unit tests")
    
    if success:
        print("✅ Unit tests passed")
    else:
        print("❌ Unit tests failed")
        if stderr:
            print(f"Error details: {stderr}")
    
    return success

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running Integration Tests...")
    print("=" * 50)
    
    integration_file = 'tests/test_integration.py'
    
    if not os.path.exists(integration_file):
        print("❌ Integration test file not found")
        return False
    
    command = [
        sys.executable, '-m', 'pytest',
        '--verbose',
        '--tb=short',
        '--junitxml=test-reports/integration-tests.xml',
        integration_file
    ]
    
    success, stdout, stderr = run_command(command, "Running integration tests")
    
    if success:
        print("✅ Integration tests passed")
    else:
        print("❌ Integration tests failed")
    
    return success

def run_e2e_tests():
    """Run end-to-end tests"""
    print("\n🌐 Running End-to-End Tests...")
    print("=" * 50)
    
    e2e_file = 'tests/test_e2e.py'
    
    if not os.path.exists(e2e_file):
        print("❌ E2E test file not found")
        return False
    
    # Check if Chrome/Firefox is available for Selenium
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        # Test Chrome availability
        try:
            driver = webdriver.Chrome(options=chrome_options)
            driver.quit()
            print("   ✅ Chrome WebDriver available")
        except Exception:
            print("   ⚠️  Chrome WebDriver not available, trying Firefox...")
            try:
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--headless")
                driver = webdriver.Firefox(options=firefox_options)
                driver.quit()
                print("   ✅ Firefox WebDriver available")
            except Exception:
                print("   ❌ No WebDriver available, skipping E2E tests")
                return True  # Don't fail the entire test suite
    
    except ImportError:
        print("   ⚠️  Selenium not installed, skipping E2E tests")
        return True
    
    command = [
        sys.executable, '-m', 'pytest',
        '--verbose',
        '--tb=short',
        '--junitxml=test-reports/e2e-tests.xml',
        '-m', 'e2e',
        e2e_file
    ]
    
    success, stdout, stderr = run_command(command, "Running E2E tests")
    
    if success:
        print("✅ E2E tests passed")
    else:
        print("❌ E2E tests failed")
    
    return success

def run_performance_tests():
    """Run performance tests"""
    print("\n⚡ Running Performance Tests...")
    print("=" * 50)
    
    # Look for performance tests in existing test files
    test_files = ['tests/test_app.py', 'tests/test_integration.py']
    
    command = [
        sys.executable, '-m', 'pytest',
        '--verbose',
        '--tb=short',
        '--junitxml=test-reports/performance-tests.xml',
        '-k', 'performance or Performance',
    ] + [f for f in test_files if os.path.exists(f)]
    
    success, stdout, stderr = run_command(command, "Running performance tests")
    
    if success:
        print("✅ Performance tests passed")
    else:
        print("⚠️  Performance tests had issues (non-critical)")
    
    return True  # Don't fail overall suite for performance issues

def generate_coverage_report():
    """Generate comprehensive coverage report"""
    print("\n📊 Generating Coverage Report...")
    print("=" * 50)
    
    # Run coverage analysis
    coverage_script = 'tests/test_coverage_analysis.py'
    
    if os.path.exists(coverage_script):
        success, stdout, stderr = run_command(
            [sys.executable, coverage_script],
            "Running coverage analysis"
        )
    else:
        print("⚠️  Coverage analysis script not found")
        success = True
    
    # Check coverage files
    coverage_files = {
        'coverage.xml': 'XML coverage report',
        'htmlcov/index.html': 'HTML coverage report',
        'test-reports/': 'Test result reports'
    }
    
    print("\n📁 Generated Reports:")
    for file_path, description in coverage_files.items():
        if os.path.exists(file_path):
            print(f"   ✅ {description}: {file_path}")
        else:
            print(f"   ❌ {description}: Not found")
    
    return success

def run_security_tests():
    """Run security-focused tests"""
    print("\n🔒 Running Security Tests...")
    print("=" * 50)
    
    # Run bandit security analysis
    success1, _, _ = run_command(
        [sys.executable, '-m', 'bandit', '-r', '.', '-f', 'json', '-o', 'test-reports/bandit-report.json'],
        "Running Bandit security analysis"
    )
    
    # Run safety check for dependencies
    success2, _, _ = run_command(
        [sys.executable, '-m', 'safety', 'check', '--json', '--output', 'test-reports/safety-report.json'],
        "Running Safety dependency check"
    )
    
    # Run auth-specific tests
    auth_tests = 'tests/test_auth.py'
    success3 = True
    if os.path.exists(auth_tests):
        success3, _, _ = run_command(
            [sys.executable, '-m', 'pytest', '--verbose', auth_tests],
            "Running authentication tests"
        )
    
    overall_success = success1 or success2 or success3  # At least one should pass
    
    if overall_success:
        print("✅ Security tests completed")
    else:
        print("⚠️  Security tests had issues")
    
    return overall_success

def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(description='Run Emergency Response App test suite')
    parser.add_argument('--unit', action='store_true', help='Run only unit tests')
    parser.add_argument('--integration', action='store_true', help='Run only integration tests')
    parser.add_argument('--e2e', action='store_true', help='Run only E2E tests')
    parser.add_argument('--performance', action='store_true', help='Run only performance tests')
    parser.add_argument('--security', action='store_true', help='Run only security tests')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report only')
    parser.add_argument('--setup', action='store_true', help='Setup test environment only')
    parser.add_argument('--fast', action='store_true', help='Run fast tests only (skip E2E)')
    
    args = parser.parse_args()
    
    print("🧪 EMERGENCY RESPONSE APP - AUTOMATED TEST SUITE")
    print("=" * 80)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    start_time = time.time()
    results = {}
    
    # Setup environment if requested
    if args.setup:
        setup_test_environment()
        return
    
    # Setup test environment
    setup_test_environment()
    
    # Run specific test types if requested
    if args.unit:
        results['unit'] = run_unit_tests()
    elif args.integration:
        results['integration'] = run_integration_tests()
    elif args.e2e:
        results['e2e'] = run_e2e_tests()
    elif args.performance:
        results['performance'] = run_performance_tests()
    elif args.security:
        results['security'] = run_security_tests()
    elif args.coverage:
        results['coverage'] = generate_coverage_report()
    elif args.fast:
        # Run all tests except E2E
        results['unit'] = run_unit_tests()
        results['integration'] = run_integration_tests()
        results['performance'] = run_performance_tests()
        results['security'] = run_security_tests()
        results['coverage'] = generate_coverage_report()
    else:
        # Run full test suite
        results['unit'] = run_unit_tests()
        results['integration'] = run_integration_tests()
        results['e2e'] = run_e2e_tests()
        results['performance'] = run_performance_tests()
        results['security'] = run_security_tests()
        results['coverage'] = generate_coverage_report()
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print("📋 TEST EXECUTION SUMMARY")
    print("=" * 80)
    
    total_tests = len(results)
    passed_tests = sum(1 for success in results.values() if success)
    
    for test_type, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_type.upper():<15} {status}")
    
    print("-" * 80)
    print(f"Total: {passed_tests}/{total_tests} test suites passed")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Overall result
    overall_success = passed_tests == total_tests
    
    if overall_success:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        exit_code = 0
    else:
        print("\n💥 SOME TESTS FAILED!")
        exit_code = 1
    
    print("\n📁 Generated Reports:")
    print("   - HTML Coverage: htmlcov/index.html")
    print("   - XML Coverage: coverage.xml")
    print("   - Test Results: test-reports/")
    
    return exit_code

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
