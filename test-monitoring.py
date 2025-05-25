#!/usr/bin/env python3
"""
Test script to generate sample data for monitoring the Emergency Response App
This script simulates user activity and emergency reports to demonstrate monitoring capabilities
"""

import requests
import time
import random
import json
from datetime import datetime

# Configuration
APP_URL = "http://localhost:3000"
METRICS_URL = f"{APP_URL}/metrics"
HEALTH_URL = f"{APP_URL}/health"
REPORT_URL = f"{APP_URL}/report-emergency"

# Sample emergency data
EMERGENCY_SEVERITIES = ["low", "medium", "high", "critical"]
EMERGENCY_LOCATIONS = [
    "Downtown Yaoundé", "Douala Port Area", "Bamenda Market", 
    "Garoua Industrial Zone", "Bafoussam City Center"
]
EMERGENCY_DESCRIPTIONS = [
    "Small kitchen fire in residential building",
    "Vehicle fire on main highway",
    "Brush fire near residential area",
    "Large warehouse fire with smoke",
    "Critical apartment building fire with people trapped"
]

# Pages to visit for generating page view metrics
PAGES_TO_VISIT = [
    "/", "/landing", "/first-aid", "/map", "/messages", 
    "/help", "/settings", "/privacy", "/guidelines",
    "/first-aid/1", "/first-aid/2", "/first-aid/3"
]

def check_app_health():
    """Check if the app is running and healthy"""
    try:
        response = requests.get(HEALTH_URL, timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print(f"✅ App is healthy - Health Score: {health_data.get('system_health_score', 'N/A')}")
            return True
        else:
            print(f"❌ App health check failed - Status: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to app: {e}")
        return False

def generate_page_views(num_views=10):
    """Generate random page views to simulate user activity"""
    print(f"\n📊 Generating {num_views} page views...")
    
    for i in range(num_views):
        page = random.choice(PAGES_TO_VISIT)
        try:
            response = requests.get(f"{APP_URL}{page}", timeout=5)
            if response.status_code == 200:
                print(f"  ✅ Visited {page}")
            else:
                print(f"  ❌ Failed to visit {page} - Status: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error visiting {page}: {e}")
        
        # Random delay between page views
        time.sleep(random.uniform(0.5, 2.0))

def generate_emergency_reports(num_reports=5):
    """Generate sample emergency reports"""
    print(f"\n🚨 Generating {num_reports} emergency reports...")
    
    for i in range(num_reports):
        # Create realistic emergency data
        severity = random.choice(EMERGENCY_SEVERITIES)
        location = random.choice(EMERGENCY_LOCATIONS)
        description = random.choice(EMERGENCY_DESCRIPTIONS)
        
        # Adjust description based on severity
        if severity == "critical":
            description = "Critical apartment building fire with people trapped"
        elif severity == "high":
            description = "Large warehouse fire with heavy smoke"
        elif severity == "medium":
            description = "Vehicle fire on main highway"
        else:
            description = "Small kitchen fire in residential building"
        
        emergency_data = {
            "location": location,
            "description": description,
            "severity": severity,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            response = requests.post(
                REPORT_URL, 
                json=emergency_data,
                headers={"Content-Type": "application/json"},
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"  🚨 {severity.upper()} emergency reported: {location}")
                print(f"     Description: {description}")
                print(f"     Status: {result.get('status', 'unknown')}")
            else:
                print(f"  ❌ Failed to report emergency - Status: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error reporting emergency: {e}")
        
        # Delay between reports (critical emergencies reported faster)
        if severity == "critical":
            time.sleep(random.uniform(1, 3))
        else:
            time.sleep(random.uniform(2, 5))

def check_metrics():
    """Check and display current metrics"""
    print("\n📈 Checking current metrics...")
    
    try:
        response = requests.get(METRICS_URL, timeout=10)
        if response.status_code == 200:
            metrics_text = response.text
            
            # Extract some key metrics
            lines = metrics_text.split('\n')
            emergency_reports = [line for line in lines if 'emergency_reports_total' in line and not line.startswith('#')]
            page_views = [line for line in lines if 'page_views_total' in line and not line.startswith('#')]
            first_aid_views = [line for line in lines if 'first_aid_views_total' in line and not line.startswith('#')]
            system_health = [line for line in lines if 'system_health_score' in line and not line.startswith('#')]
            active_users = [line for line in lines if 'active_users' in line and not line.startswith('#')]
            
            print("  📊 Key Metrics:")
            
            if emergency_reports:
                print("    🚨 Emergency Reports:")
                for metric in emergency_reports[:5]:  # Show first 5
                    print(f"      {metric}")
            
            if page_views:
                print("    📄 Page Views:")
                for metric in page_views[:5]:  # Show first 5
                    print(f"      {metric}")
            
            if system_health:
                print("    💚 System Health:")
                for metric in system_health:
                    print(f"      {metric}")
            
            if active_users:
                print("    👥 Active Users:")
                for metric in active_users:
                    print(f"      {metric}")
                    
        else:
            print(f"  ❌ Failed to get metrics - Status: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"  ❌ Error getting metrics: {e}")

def simulate_user_session():
    """Simulate a realistic user session"""
    print("\n👤 Simulating user session...")
    
    # User journey: Welcome -> Landing -> First Aid -> Specific Guide -> Help
    user_journey = [
        "/",
        "/landing", 
        "/first-aid",
        f"/first-aid/{random.randint(1, 10)}",
        "/help"
    ]
    
    for page in user_journey:
        try:
            response = requests.get(f"{APP_URL}{page}", timeout=5)
            if response.status_code == 200:
                print(f"  📱 User visited: {page}")
            time.sleep(random.uniform(2, 8))  # Realistic reading time
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Error in user journey: {e}")

def main():
    """Main function to run monitoring tests"""
    print("🔥 Emergency Response App - Monitoring Test Script")
    print("=" * 60)
    
    # Check if app is running
    if not check_app_health():
        print("\n❌ App is not running. Please start the app first:")
        print("   python app.py")
        return
    
    print("\n🎯 Starting monitoring demonstration...")
    
    try:
        # Phase 1: Generate some baseline activity
        print("\n📊 Phase 1: Generating baseline user activity")
        simulate_user_session()
        generate_page_views(8)
        
        # Phase 2: Generate emergency reports
        print("\n🚨 Phase 2: Simulating emergency reports")
        generate_emergency_reports(3)
        
        # Phase 3: More user activity
        print("\n👥 Phase 3: More user activity")
        generate_page_views(12)
        
        # Phase 4: Critical emergency simulation
        print("\n🚨 Phase 4: Critical emergency simulation")
        critical_emergency = {
            "location": "Downtown Yaoundé - Central Hospital",
            "description": "Major fire at hospital with patients requiring immediate evacuation",
            "severity": "critical",
            "timestamp": datetime.now().isoformat()
        }
        
        response = requests.post(
            REPORT_URL, 
            json=critical_emergency,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code == 200:
            print("  🚨 CRITICAL EMERGENCY REPORTED!")
            print("     This should trigger immediate alerts in monitoring systems")
        
        # Phase 5: Check final metrics
        print("\n📈 Phase 5: Final metrics check")
        check_metrics()
        
        # Final health check
        print("\n🏥 Final health check")
        check_app_health()
        
        print("\n✅ Monitoring test completed!")
        print("\n📊 You can now check:")
        print(f"   • Prometheus: http://localhost:9090")
        print(f"   • Grafana: http://localhost:3001 (admin/admin123)")
        print(f"   • App Health: {HEALTH_URL}")
        print(f"   • App Metrics: {METRICS_URL}")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
