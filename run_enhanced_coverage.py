#!/usr/bin/env python3
"""
Enhanced Coverage Analysis Script
Runs comprehensive tests to achieve 85%+ code coverage
"""

import os
import sys
import subprocess
import time
import json
import xml.etree.ElementTree as ET
from pathlib import Path

def run_command(command, description="", timeout=300):
    """Run a command and return success status"""
    print(f"\n🔧 {description}")
    print(f"   Command: {' '.join(command)}")
    
    try:
        result = subprocess.run(
            command, 
            capture_output=True, 
            text=True,
            timeout=timeout
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
        print(f"   ⏰ Timeout after {timeout} seconds")
        return False, "", "Timeout"
    except Exception as e:
        print(f"   ❌ Exception: {e}")
        return False, "", str(e)

def install_coverage_dependencies():
    """Install required coverage dependencies"""
    print("📦 Installing coverage dependencies...")
    
    dependencies = [
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0',
        'pytest-html>=3.0.0',
        'coverage>=7.0.0',
        'pytest-xdist>=3.0.0',
        'flask-cors>=4.0.0'
    ]
    
    for dep in dependencies:
        success, _, _ = run_command(
            [sys.executable, '-m', 'pip', 'install', dep],
            f"Installing {dep}"
        )
        if not success:
            print(f"⚠️  Warning: Failed to install {dep}")

def run_comprehensive_tests():
    """Run comprehensive test suite for maximum coverage"""
    print("\n🧪 Running Comprehensive Test Suite for 85%+ Coverage...")
    print("=" * 70)
    
    # Create necessary directories
    os.makedirs('htmlcov', exist_ok=True)
    os.makedirs('test-reports', exist_ok=True)
    
    # Enhanced pytest command for maximum coverage
    command = [
        sys.executable, '-m', 'pytest',
        '--verbose',
        '--tb=short',
        '--cov=.',
        '--cov-report=html:htmlcov',
        '--cov-report=xml:coverage.xml',
        '--cov-report=term-missing',
        '--cov-fail-under=85',  # Fail if coverage < 85%
        '--junitxml=test-reports/comprehensive-tests.xml',
        'tests/'
    ]
    
    success, stdout, stderr = run_command(command, "Running comprehensive tests with coverage")
    
    return success, stdout, stderr

def analyze_coverage_results():
    """Analyze coverage results and provide recommendations"""
    print("\n📊 Analyzing Coverage Results...")
    print("=" * 50)
    
    coverage_file = Path("coverage.xml")
    if not coverage_file.exists():
        print("❌ Coverage XML file not found")
        return None
    
    try:
        tree = ET.parse(coverage_file)
        root = tree.getroot()
        
        # Overall coverage
        overall_coverage = float(root.attrib.get('line-rate', '0')) * 100
        branch_coverage = float(root.attrib.get('branch-rate', '0')) * 100
        
        print(f"📈 Overall Line Coverage: {overall_coverage:.2f}%")
        print(f"📈 Overall Branch Coverage: {branch_coverage:.2f}%")
        
        # Per-file analysis
        files_analysis = []
        
        for package in root.findall('.//package'):
            for class_elem in package.findall('.//class'):
                filename = class_elem.attrib.get('filename', 'Unknown')
                line_rate = float(class_elem.attrib.get('line-rate', '0')) * 100
                
                # Skip excluded files
                if (filename.startswith('tests/') or 
                    not filename.endswith('.py') or
                    filename.startswith('venv/') or
                    filename.startswith('build/') or
                    'coverage_dashboard' in filename or
                    filename.startswith('run_')):
                    continue
                
                files_analysis.append({
                    'filename': filename,
                    'coverage': line_rate
                })
        
        # Sort by coverage (lowest first)
        files_analysis.sort(key=lambda x: x['coverage'])
        
        print(f"\n📁 File Coverage Analysis:")
        print("-" * 50)
        
        for file_info in files_analysis:
            filename = file_info['filename']
            coverage = file_info['coverage']
            
            if coverage >= 85:
                status = "✅"
            elif coverage >= 70:
                status = "⚠️ "
            else:
                status = "❌"
            
            print(f"{status} {filename:<30} {coverage:>6.2f}%")
        
        # Coverage summary
        total_files = len(files_analysis)
        files_above_85 = len([f for f in files_analysis if f['coverage'] >= 85])
        files_above_70 = len([f for f in files_analysis if f['coverage'] >= 70])
        files_below_70 = total_files - files_above_70
        
        print(f"\n📊 Coverage Summary:")
        print(f"   Total files: {total_files}")
        print(f"   Files ≥ 85%: {files_above_85} ({files_above_85/total_files*100:.1f}%)")
        print(f"   Files ≥ 70%: {files_above_70} ({files_above_70/total_files*100:.1f}%)")
        print(f"   Files < 70%: {files_below_70} ({files_below_70/total_files*100:.1f}%)")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        if overall_coverage >= 85:
            print("   🎉 Excellent! Coverage target achieved!")
        elif overall_coverage >= 80:
            print("   👍 Good coverage, close to target")
            print("   📝 Focus on files with lowest coverage")
        else:
            print("   📈 Need to improve coverage")
            print("   🎯 Add tests for uncovered code paths")
        
        # Files needing attention
        low_coverage_files = [f for f in files_analysis if f['coverage'] < 85]
        if low_coverage_files:
            print(f"\n🎯 Files needing attention (< 85% coverage):")
            for file_info in low_coverage_files[:5]:  # Show top 5
                print(f"   📄 {file_info['filename']}: {file_info['coverage']:.1f}%")
        
        return {
            'overall_coverage': overall_coverage,
            'branch_coverage': branch_coverage,
            'files': files_analysis,
            'target_met': overall_coverage >= 85
        }
        
    except Exception as e:
        print(f"❌ Error analyzing coverage: {e}")
        return None

def generate_coverage_report():
    """Generate detailed coverage report"""
    print("\n📄 Generating Coverage Reports...")
    print("=" * 40)
    
    # Check generated files
    reports = {
        'coverage.xml': 'XML coverage report',
        'htmlcov/index.html': 'HTML coverage report',
        'test-reports/comprehensive-tests.xml': 'Test results'
    }
    
    print("📁 Generated Reports:")
    for file_path, description in reports.items():
        if os.path.exists(file_path):
            print(f"   ✅ {description}: {file_path}")
        else:
            print(f"   ❌ {description}: Not found")
    
    # Generate summary JSON
    coverage_analysis = analyze_coverage_results()
    if coverage_analysis:
        summary = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'overall_coverage': coverage_analysis['overall_coverage'],
            'target_met': coverage_analysis['target_met'],
            'total_files': len(coverage_analysis['files']),
            'files_above_85': len([f for f in coverage_analysis['files'] if f['coverage'] >= 85])
        }
        
        with open('coverage-summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"   ✅ Coverage summary: coverage-summary.json")

def start_coverage_dashboard():
    """Start the coverage dashboard"""
    print("\n🌐 Starting Coverage Dashboard...")
    print("=" * 40)
    
    try:
        # Start dashboard in background
        dashboard_process = subprocess.Popen([
            sys.executable, 'coverage_dashboard.py'
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        print("   🚀 Coverage dashboard starting...")
        print("   📊 Dashboard URL: http://localhost:5001")
        print("   📊 VPS URL: http://31.97.11.49:5001")
        
        return dashboard_process
        
    except Exception as e:
        print(f"   ❌ Failed to start dashboard: {e}")
        return None

def main():
    """Main function"""
    print("🎯 ENHANCED COVERAGE ANALYSIS - TARGET: 85%+")
    print("=" * 80)
    print(f"Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    
    start_time = time.time()
    
    # Step 1: Install dependencies
    install_coverage_dependencies()
    
    # Step 2: Run comprehensive tests
    test_success, test_stdout, test_stderr = run_comprehensive_tests()
    
    # Step 3: Analyze results
    coverage_analysis = analyze_coverage_results()
    
    # Step 4: Generate reports
    generate_coverage_report()
    
    # Step 5: Start dashboard
    dashboard_process = start_coverage_dashboard()
    
    # Summary
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "=" * 80)
    print("📋 ENHANCED COVERAGE ANALYSIS SUMMARY")
    print("=" * 80)
    
    if coverage_analysis:
        overall_coverage = coverage_analysis['overall_coverage']
        target_met = coverage_analysis['target_met']
        
        print(f"📊 Overall Coverage: {overall_coverage:.2f}%")
        print(f"🎯 Target (85%): {'✅ ACHIEVED' if target_met else '❌ NOT MET'}")
        print(f"⏱️  Duration: {duration:.2f} seconds")
        
        if target_met:
            print("\n🎉 CONGRATULATIONS! 85%+ COVERAGE ACHIEVED! 🎉")
            print("🏆 Your Emergency Response App has excellent test coverage!")
        else:
            print(f"\n📈 COVERAGE IMPROVEMENT NEEDED")
            print(f"   Current: {overall_coverage:.2f}%")
            print(f"   Target:  85.00%")
            print(f"   Gap:     {85 - overall_coverage:.2f}%")
    else:
        print("❌ Coverage analysis failed")
    
    print("\n📁 Generated Reports:")
    print("   📊 HTML Report: htmlcov/index.html")
    print("   📄 XML Report: coverage.xml")
    print("   🌐 Dashboard: http://localhost:5001")
    print("   🌐 VPS Dashboard: http://31.97.11.49:5001")
    
    print("\n🚀 Next Steps:")
    print("1. Open HTML coverage report to see detailed line-by-line coverage")
    print("2. Access coverage dashboard for real-time monitoring")
    print("3. Add tests for uncovered code paths if needed")
    print("4. Deploy dashboard to VPS for team access")
    
    return coverage_analysis['target_met'] if coverage_analysis else False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
