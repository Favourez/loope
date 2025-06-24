#!/usr/bin/env python3
"""
Coverage Dashboard for Emergency Response App
Web interface to display test coverage results and metrics
"""

import os
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
import subprocess
import sqlite3

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS

# Create Flask app for coverage dashboard
coverage_app = Flask(__name__, 
                    template_folder='templates/coverage',
                    static_folder='static/coverage')
CORS(coverage_app)

def parse_coverage_xml():
    """Parse coverage.xml file and extract coverage data"""
    coverage_file = Path("coverage.xml")
    
    if not coverage_file.exists():
        return None
    
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        # Overall coverage
        overall_coverage = float(root.attrib.get('line-rate', '0')) * 100
        branch_coverage = float(root.attrib.get('branch-rate', '0')) * 100
        
        # Per-file coverage
        files_coverage = []
        
        for package in root.findall('.//package'):
            for class_elem in package.findall('.//class'):
                filename = class_elem.attrib.get('filename', 'Unknown')
                line_rate = float(class_elem.attrib.get('line-rate', '0')) * 100
                branch_rate = float(class_elem.attrib.get('branch-rate', '0')) * 100
                
                # Skip test files and non-Python files
                if (filename.startswith('tests/') or 
                    not filename.endswith('.py') or
                    filename.startswith('venv/') or
                    filename.startswith('build/')):
                    continue
                
                # Get line details
                lines = class_elem.findall('.//line')
                total_lines = len(lines)
                covered_lines = len([line for line in lines if line.attrib.get('hits', '0') != '0'])
                
                files_coverage.append({
                    'filename': filename,
                    'line_coverage': line_rate,
                    'branch_coverage': branch_rate,
                    'total_lines': total_lines,
                    'covered_lines': covered_lines,
                    'status': 'good' if line_rate >= 85 else 'warning' if line_rate >= 70 else 'poor'
                })
        
        return {
            'overall_line_coverage': overall_coverage,
            'overall_branch_coverage': branch_coverage,
            'files': sorted(files_coverage, key=lambda x: x['line_coverage'], reverse=True),
            'timestamp': datetime.now().isoformat(),
            'total_files': len(files_coverage),
            'files_above_85': len([f for f in files_coverage if f['line_coverage'] >= 85]),
            'files_above_70': len([f for f in files_coverage if f['line_coverage'] >= 70])
        }
    
    except Exception as e:
        print(f"Error parsing coverage XML: {e}")
        return None

def get_test_results():
    """Get test execution results"""
    test_results = {
        'total_tests': 0,
        'passed_tests': 0,
        'failed_tests': 0,
        'skipped_tests': 0,
        'test_files': [],
        'last_run': None
    }
    
    # Check for JUnit XML files
    test_reports_dir = Path("test-reports")
    if test_reports_dir.exists():
        for xml_file in test_reports_dir.glob("*.xml"):
            try:
                tree = ET.parse(xml_file)
                root = tree.getroot()
                
                # Extract test statistics
                tests = int(root.attrib.get('tests', '0'))
                failures = int(root.attrib.get('failures', '0'))
                errors = int(root.attrib.get('errors', '0'))
                skipped = int(root.attrib.get('skipped', '0'))
                
                test_results['total_tests'] += tests
                test_results['failed_tests'] += failures + errors
                test_results['skipped_tests'] += skipped
                test_results['passed_tests'] += tests - failures - errors - skipped
                
                test_results['test_files'].append({
                    'name': xml_file.stem,
                    'tests': tests,
                    'passed': tests - failures - errors - skipped,
                    'failed': failures + errors,
                    'skipped': skipped
                })
                
            except Exception as e:
                print(f"Error parsing test results {xml_file}: {e}")
    
    return test_results

def run_coverage_analysis():
    """Run coverage analysis and return results"""
    try:
        # Run tests with coverage
        result = subprocess.run([
            'python', '-m', 'pytest',
            '--cov=.',
            '--cov-report=xml:coverage.xml',
            '--cov-report=html:htmlcov',
            '--junitxml=test-reports/coverage-run.xml',
            'tests/'
        ], capture_output=True, text=True, timeout=300)
        
        return {
            'success': result.returncode == 0,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'timestamp': datetime.now().isoformat()
        }
    
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Coverage analysis timed out',
            'timestamp': datetime.now().isoformat()
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

@coverage_app.route('/')
def dashboard():
    """Main coverage dashboard"""
    coverage_data = parse_coverage_xml()
    test_results = get_test_results()
    
    return render_template('coverage_dashboard.html',
                         coverage=coverage_data,
                         tests=test_results)

@coverage_app.route('/api/coverage')
def api_coverage():
    """API endpoint for coverage data"""
    coverage_data = parse_coverage_xml()
    return jsonify(coverage_data)

@coverage_app.route('/api/tests')
def api_tests():
    """API endpoint for test results"""
    test_results = get_test_results()
    return jsonify(test_results)

@coverage_app.route('/api/run-coverage', methods=['POST'])
def api_run_coverage():
    """API endpoint to trigger coverage analysis"""
    result = run_coverage_analysis()
    return jsonify(result)

@coverage_app.route('/api/status')
def api_status():
    """API endpoint for dashboard status"""
    coverage_data = parse_coverage_xml()
    test_results = get_test_results()
    
    status = {
        'coverage_available': coverage_data is not None,
        'overall_coverage': coverage_data['overall_line_coverage'] if coverage_data else 0,
        'target_met': coverage_data['overall_line_coverage'] >= 85 if coverage_data else False,
        'total_tests': test_results['total_tests'],
        'test_success_rate': (test_results['passed_tests'] / test_results['total_tests'] * 100) if test_results['total_tests'] > 0 else 0,
        'last_updated': datetime.now().isoformat()
    }
    
    return jsonify(status)

@coverage_app.route('/files/<path:filename>')
def file_coverage(filename):
    """Show coverage details for a specific file"""
    coverage_data = parse_coverage_xml()
    
    if not coverage_data:
        return "Coverage data not available", 404
    
    file_data = None
    for file_info in coverage_data['files']:
        if file_info['filename'] == filename:
            file_data = file_info
            break
    
    if not file_data:
        return "File not found in coverage data", 404
    
    return render_template('file_coverage.html',
                         file=file_data,
                         filename=filename)

@coverage_app.route('/trends')
def coverage_trends():
    """Show coverage trends over time"""
    # This would typically read from a database of historical coverage data
    # For now, return current data
    coverage_data = parse_coverage_xml()
    
    return render_template('coverage_trends.html',
                         coverage=coverage_data)

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('templates/coverage', exist_ok=True)
    os.makedirs('static/coverage', exist_ok=True)
    os.makedirs('test-reports', exist_ok=True)
    
    print("🔍 Coverage Dashboard Starting...")
    print("📊 Dashboard URL: http://localhost:5001")
    print("📈 API Endpoints:")
    print("   - GET  /api/coverage     - Coverage data")
    print("   - GET  /api/tests        - Test results")
    print("   - POST /api/run-coverage - Run coverage analysis")
    print("   - GET  /api/status       - Dashboard status")
    
    coverage_app.run(host='0.0.0.0', port=5001, debug=True)
