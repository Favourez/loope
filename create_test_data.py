#!/usr/bin/env python3
"""
Script to create test data for the emergency response application
"""

from database import create_user, create_emergency_report
import sys

def create_test_users():
    """Create test users and fire departments"""
    
    try:
        # Create a regular user
        user_id = create_user(
            username="testuser",
            email="user@test.com",
            password="password123",
            user_type="user",
            full_name="John Doe",
            phone="+237123456789"
        )
        print(f"Created regular user with ID: {user_id}")
        
        # Create a fire department
        dept_id = create_user(
            username="yaoundefire",
            email="fire@yaounde.cm",
            password="firepass123",
            user_type="fire_department",
            full_name="Fire Chief Marie Ngozi",
            phone="+237118001",
            department_name="Yaoundé Central Fire Department",
            department_location="Yaoundé, Centre Region"
        )
        print(f"Created fire department with ID: {dept_id}")
        
        # Create another fire department
        dept_id2 = create_user(
            username="doualafire",
            email="fire@douala.cm",
            password="firepass123",
            user_type="fire_department",
            full_name="Fire Chief Paul Mbeki",
            phone="+237118002",
            department_name="Douala Port Fire Department",
            department_location="Douala, Littoral Region"
        )
        print(f"Created second fire department with ID: {dept_id2}")
        
        # Create some emergency reports
        report1 = create_emergency_report(
            user_id=user_id,
            location="Bastos, Yaoundé",
            description="House fire in residential area, smoke visible from street",
            severity="high",
            latitude=3.8691,
            longitude=11.5174
        )
        print(f"Created emergency report with ID: {report1}")
        
        report2 = create_emergency_report(
            user_id=user_id,
            location="Douala Port Area",
            description="Vehicle fire near container terminal",
            severity="medium",
            latitude=4.0511,
            longitude=9.7679
        )
        print(f"Created emergency report with ID: {report2}")
        
        report3 = create_emergency_report(
            user_id=user_id,
            location="Bamenda Market",
            description="Small fire in market stall, contained but needs attention",
            severity="low",
            latitude=5.9631,
            longitude=10.1591
        )
        print(f"Created emergency report with ID: {report3}")
        
        print("\n✅ Test data created successfully!")
        print("\nTest Accounts:")
        print("Regular User:")
        print("  Username: testuser")
        print("  Password: password123")
        print("\nFire Department (Yaoundé):")
        print("  Username: yaoundefire")
        print("  Password: firepass123")
        print("\nFire Department (Douala):")
        print("  Username: doualafire")
        print("  Password: firepass123")
        
    except ValueError as e:
        print(f"❌ Error creating test data: {e}")
        print("Note: Test users might already exist. Try different usernames or delete the database file.")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    create_test_users()
