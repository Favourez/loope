#!/usr/bin/env python3
"""
Test script to create emergency reports with GPS location data
"""

from database import create_emergency_report, get_user_by_username
import random

def create_test_emergency_with_location():
    """Create test emergency reports with GPS coordinates"""
    
    # Get a test user
    user = get_user_by_username("testuser")
    if not user:
        print("❌ Test user 'testuser' not found. Please run create_test_data.py first.")
        return
    
    # Sample locations in Cameroon with GPS coordinates
    test_emergencies = [
        {
            "location": "Bastos Residential Area, Yaoundé",
            "description": "House fire spreading rapidly, multiple families evacuating. Thick black smoke visible from main road.",
            "severity": "critical",
            "latitude": 3.8691,
            "longitude": 11.5174,
            "accuracy": 15.0
        },
        {
            "location": "Douala Port Container Terminal",
            "description": "Vehicle fire in parking area, no injuries reported but fire spreading to nearby vehicles.",
            "severity": "high",
            "latitude": 4.0511,
            "longitude": 9.7679,
            "accuracy": 8.0
        },
        {
            "location": "Bamenda Commercial Avenue",
            "description": "Small electrical fire in shop, contained but needs professional attention.",
            "severity": "medium",
            "latitude": 5.9631,
            "longitude": 10.1591,
            "accuracy": 25.0
        },
        {
            "location": "Garoua Market Square",
            "description": "Trash fire near market stalls, low risk but creating smoke hazard.",
            "severity": "low",
            "latitude": 9.3265,
            "longitude": 13.3981,
            "accuracy": 12.0
        }
    ]
    
    print("Creating test emergency reports with GPS location data...")
    
    for i, emergency in enumerate(test_emergencies, 1):
        try:
            report_id = create_emergency_report(
                user_id=user['id'],
                location=emergency['location'],
                description=emergency['description'],
                severity=emergency['severity'],
                latitude=emergency['latitude'],
                longitude=emergency['longitude'],
                location_accuracy=emergency['accuracy']
            )
            
            print(f"✅ Created emergency report #{report_id}")
            print(f"   Location: {emergency['location']}")
            print(f"   GPS: {emergency['latitude']}, {emergency['longitude']} (±{emergency['accuracy']}m)")
            print(f"   Severity: {emergency['severity'].upper()}")
            print(f"   Description: {emergency['description'][:60]}...")
            print()
            
        except Exception as e:
            print(f"❌ Error creating emergency report {i}: {e}")
    
    print("🎯 Test emergency reports created successfully!")
    print("\nNow you can:")
    print("1. Login as a fire department user (yaoundefire / firepass123)")
    print("2. View the emergency reports with GPS coordinates")
    print("3. Test the location features (maps, directions, etc.)")
    print("4. Update report statuses")

if __name__ == "__main__":
    create_test_emergency_with_location()
