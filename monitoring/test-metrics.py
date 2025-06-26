#!/usr/bin/env python3
"""
Test script to generate sample metrics for the Emergency Response App
This script will make requests to various endpoints to generate monitoring data
"""

import requests
import time
import random
import json
from concurrent.futures import ThreadPoolExecutor
import threading

BASE_URL = "http://31.97.11.49"

def make_request(endpoint, method="GET", data=None):
    """Make HTTP request to the application"""
    try:
        url = f"{BASE_URL}{endpoint}"
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        
        print(f"✅ {method} {endpoint} - Status: {response.status_code}")
        return response.status_code
    except Exception as e:
        print(f"❌ {method} {endpoint} - Error: {str(e)}")
        return None

def simulate_page_views():
    """Simulate various page views"""
    pages = ["/", "/register", "/first-aid", "/map", "/medical-chatbot", "/profile", "/messages"]
    
    for _ in range(10):
        page = random.choice(pages)
        make_request(page)
        time.sleep(random.uniform(0.5, 2.0))

def simulate_emergency_reports():
    """Simulate emergency report submissions"""
    emergency_data = {
        "type": "fire",
        "severity": random.choice(["low", "medium", "high", "critical"]),
        "location": f"Test Location {random.randint(1, 100)}",
        "description": "Test emergency report for monitoring",
        "latitude": random.uniform(-90, 90),
        "longitude": random.uniform(-180, 180)
    }
    
    make_request("/report-emergency", "POST", emergency_data)

def simulate_first_aid_views():
    """Simulate first aid guide views"""
    practices = [
        {"id": 1, "name": "CPR"},
        {"id": 2, "name": "Choking"},
        {"id": 3, "name": "Burns"},
        {"id": 4, "name": "Bleeding"},
        {"id": 5, "name": "Fractures"}
    ]
    
    for _ in range(5):
        practice = random.choice(practices)
        make_request(f"/first-aid/{practice['id']}")
        time.sleep(random.uniform(1, 3))

def check_health():
    """Check application health"""
    make_request("/health")

def generate_load():
    """Generate continuous load for monitoring"""
    print("🚀 Starting metrics generation for Emergency Response App monitoring...")
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        while True:
            try:
                # Submit various tasks
                executor.submit(simulate_page_views)
                executor.submit(check_health)
                
                # Occasionally simulate emergency reports
                if random.random() < 0.3:
                    executor.submit(simulate_emergency_reports)
                
                # Simulate first aid views
                if random.random() < 0.4:
                    executor.submit(simulate_first_aid_views)
                
                # Wait before next batch
                time.sleep(random.uniform(5, 15))
                
            except KeyboardInterrupt:
                print("\n🛑 Stopping metrics generation...")
                break
            except Exception as e:
                print(f"❌ Error in load generation: {str(e)}")
                time.sleep(5)

if __name__ == "__main__":
    print("📊 Emergency Response App - Metrics Generator")
    print("=" * 50)
    print(f"Target URL: {BASE_URL}")
    print("This will generate sample data for Prometheus/Grafana monitoring")
    print("Press Ctrl+C to stop")
    print("=" * 50)
    
    generate_load()
