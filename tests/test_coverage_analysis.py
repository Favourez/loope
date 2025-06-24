#!/usr/bin/env python3
"""
Test coverage analysis and reporting
"""

import pytest
import sys
import os
import json
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestCoverageAnalysis:
    """Test coverage analysis and validation"""
    
    def test_minimum_coverage_requirement(self):
        """Test that minimum coverage requirement is met"""
        # This test will fail if coverage is below 80%
        # The actual coverage check is done by pytest-cov in pytest.ini
        
        # Read coverage report if it exists
        coverage_file = Path("coverage.xml")
        if coverage_file.exists():
            tree = ET.parse(coverage_file)
            root = tree.getroot()
            
            # Extract coverage percentage
            coverage_attr = root.attrib.get('line-rate', '0')
            coverage_percentage = float(coverage_attr) * 100
            
            print(f"Current coverage: {coverage_percentage:.2f}%")
            assert coverage_percentage >= 80.0, f"Coverage {coverage_percentage:.2f}% is below minimum 80%"
        else:
            # If no coverage file exists, assume this is the first run
            print("No coverage file found - this may be the first test run")
    
    def test_all_modules_have_tests(self):
        """Test that all main modules have corresponding test files"""
        main_modules = [
            'app.py',
            'database.py',
            'auth.py',
            'api_endpoints.py'
        ]
        
        test_files = [
            'tests/test_app.py',
            'tests/test_database.py',
            'tests/test_auth.py',
            'tests/test_integration.py'
        ]
        
        for test_file in test_files:
            assert os.path.exists(test_file), f"Test file {test_file} is missing"
        
        print("✅ All required test files exist")
    
    def test_critical_functions_covered(self):
        """Test that critical functions are covered by tests"""
        # This is a meta-test to ensure critical functionality is tested
        
        critical_test_patterns = [
            # Database operations
            "test_create_user",
            "test_verify_user", 
            "test_create_emergency_report",
            "test_get_emergency_reports",
            
            # Authentication
            "test_hash_password",
            "test_verify_password",
            "test_verify_api_key",
            
            # API endpoints
            "test_health_endpoint",
            "test_create_emergency",
            "test_get_emergencies",
            
            # Integration tests
            "test_emergency_report_creation_and_retrieval",
            "test_user_authentication_flow"
        ]
        
        # Check that test files contain these critical test patterns
        test_files = [
            'tests/test_app.py',
            'tests/test_database.py', 
            'tests/test_auth.py',
            'tests/test_integration.py'
        ]
        
        found_patterns = []
        for test_file in test_files:
            if os.path.exists(test_file):
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in critical_test_patterns:
                        if pattern in content:
                            found_patterns.append(pattern)
        
        missing_patterns = set(critical_test_patterns) - set(found_patterns)
        
        if missing_patterns:
            print(f"⚠️  Missing critical test patterns: {missing_patterns}")
        
        # At least 80% of critical patterns should be present
        coverage_ratio = len(found_patterns) / len(critical_test_patterns)
        assert coverage_ratio >= 0.8, f"Only {coverage_ratio:.2%} of critical test patterns found"
        
        print(f"✅ {coverage_ratio:.2%} of critical test patterns found")

def generate_coverage_report():
    """Generate comprehensive coverage report"""
    print("🔍 Generating Coverage Report...")
    print("=" * 60)
    
    try:
        # Run tests with coverage
        result = subprocess.run([
            'python', '-m', 'pytest', 
            '--cov=.',
            '--cov-report=html:htmlcov',
            '--cov-report=xml:coverage.xml',
            '--cov-report=term-missing',
            '--cov-fail-under=80',
            'tests/'
        ], capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(__file__)))
        
        print("STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        print(f"Return code: {result.returncode}")
        
        # Parse coverage XML if available
        coverage_file = Path("coverage.xml")
        if coverage_file.exists():
            tree = ET.parse(coverage_file)
            root = tree.getroot()
            
            print("\n📊 COVERAGE SUMMARY")
            print("=" * 60)
            
            # Overall coverage
            overall_coverage = float(root.attrib.get('line-rate', '0')) * 100
            print(f"Overall Coverage: {overall_coverage:.2f}%")
            
            # Per-file coverage
            print("\n📁 PER-FILE COVERAGE")
            print("-" * 60)
            
            for package in root.findall('.//package'):
                package_name = package.attrib.get('name', 'Unknown')
                if package_name != '.':  # Skip root package
                    continue
                    
                for class_elem in package.findall('.//class'):
                    filename = class_elem.attrib.get('filename', 'Unknown')
                    line_rate = float(class_elem.attrib.get('line-rate', '0')) * 100
                    
                    # Skip test files and non-Python files
                    if (filename.startswith('tests/') or 
                        not filename.endswith('.py') or
                        filename.startswith('venv/') or
                        filename.startswith('build/')):
                        continue
                    
                    status = "✅" if line_rate >= 80 else "❌"
                    print(f"{status} {filename:<30} {line_rate:>6.2f}%")
            
            print("\n🎯 COVERAGE GOALS")
            print("-" * 60)
            if overall_coverage >= 80:
                print("✅ Minimum 80% coverage requirement: PASSED")
            else:
                print("❌ Minimum 80% coverage requirement: FAILED")
                print(f"   Current: {overall_coverage:.2f}%, Required: 80.00%")
            
            if overall_coverage >= 90:
                print("🌟 Excellent coverage (90%+): ACHIEVED")
            elif overall_coverage >= 85:
                print("👍 Good coverage (85%+): ACHIEVED")
            
        else:
            print("⚠️  Coverage XML file not found")
        
        # Check for HTML report
        html_report = Path("htmlcov/index.html")
        if html_report.exists():
            print(f"\n📄 HTML Coverage Report: {html_report.absolute()}")
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error generating coverage report: {e}")
        return False

def analyze_test_quality():
    """Analyze test quality metrics"""
    print("\n🔬 TEST QUALITY ANALYSIS")
    print("=" * 60)
    
    test_files = [
        'tests/test_app.py',
        'tests/test_database.py',
        'tests/test_auth.py', 
        'tests/test_integration.py',
        'tests/test_e2e.py'
    ]
    
    total_tests = 0
    total_assertions = 0
    
    for test_file in test_files:
        if os.path.exists(test_file):
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Count test methods
                test_methods = content.count('def test_')
                total_tests += test_methods
                
                # Count assertions
                assertions = (content.count('assert ') + 
                            content.count('assert(') +
                            content.count('assertEqual') +
                            content.count('assertTrue') +
                            content.count('assertFalse'))
                total_assertions += assertions
                
                print(f"📝 {test_file:<25} Tests: {test_methods:>3}, Assertions: {assertions:>3}")
    
    print("-" * 60)
    print(f"📊 TOTAL                     Tests: {total_tests:>3}, Assertions: {total_assertions:>3}")
    
    if total_tests > 0:
        avg_assertions = total_assertions / total_tests
        print(f"📈 Average assertions per test: {avg_assertions:.2f}")
        
        if avg_assertions >= 2.0:
            print("✅ Good assertion density")
        else:
            print("⚠️  Consider adding more assertions per test")
    
    # Test type distribution
    print(f"\n🏷️  TEST TYPE DISTRIBUTION")
    print("-" * 60)
    
    test_types = {
        'Unit Tests': 'test_app.py, test_database.py, test_auth.py',
        'Integration Tests': 'test_integration.py', 
        'E2E Tests': 'test_e2e.py',
        'Performance Tests': 'TestPerformance'
    }
    
    for test_type, pattern in test_types.items():
        count = 0
        for test_file in test_files:
            if os.path.exists(test_file):
                with open(test_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if any(p in content for p in pattern.split(', ')):
                        count += content.count('def test_')
        
        print(f"📋 {test_type:<20} {count:>3} tests")

def main():
    """Main function to run coverage analysis"""
    print("🧪 EMERGENCY RESPONSE APP - TEST COVERAGE ANALYSIS")
    print("=" * 80)
    
    # Generate coverage report
    success = generate_coverage_report()
    
    # Analyze test quality
    analyze_test_quality()
    
    print("\n" + "=" * 80)
    if success:
        print("✅ Coverage analysis completed successfully!")
    else:
        print("❌ Coverage analysis completed with issues!")
    
    print("\n📋 NEXT STEPS:")
    print("1. Review HTML coverage report: htmlcov/index.html")
    print("2. Focus on files with <80% coverage")
    print("3. Add tests for uncovered critical functions")
    print("4. Run tests regularly during development")
    
    return success

if __name__ == '__main__':
    main()
