#!/usr/bin/env python3
"""
Script to create fire department accounts
"""

from database import create_user

def create_fire_departments():
    """Create fire department accounts"""
    
    fire_departments = [
        {
            "username": "yaoundefire",
            "email": "fire@yaounde.cm",
            "password": "firepass123",
            "full_name": "Fire Chief Marie Ngozi",
            "phone": "+237118001",
            "department_name": "Yaoundé Central Fire Department",
            "department_location": "Yaoundé, Centre Region"
        },
        {
            "username": "doualafire",
            "email": "fire@douala.cm",
            "password": "firepass123",
            "full_name": "Fire Chief Paul Mbeki",
            "phone": "+237118002",
            "department_name": "Douala Port Fire Department",
            "department_location": "Douala, Littoral Region"
        }
    ]
    
    for dept in fire_departments:
        try:
            dept_id = create_user(
                username=dept["username"],
                email=dept["email"],
                password=dept["password"],
                user_type="fire_department",
                full_name=dept["full_name"],
                phone=dept["phone"],
                department_name=dept["department_name"],
                department_location=dept["department_location"]
            )
            print(f"✅ Created fire department: {dept['department_name']} (ID: {dept_id})")
            print(f"   Username: {dept['username']}")
            print(f"   Email: {dept['email']}")
            print(f"   Password: {dept['password']}")
            print()
            
        except ValueError as e:
            if "already exists" in str(e):
                print(f"ℹ️  Fire department {dept['username']} already exists")
            else:
                print(f"❌ Error creating {dept['username']}: {e}")
        except Exception as e:
            print(f"❌ Unexpected error creating {dept['username']}: {e}")

if __name__ == "__main__":
    print("🚒 Creating Fire Department Accounts...")
    print("="*50)
    create_fire_departments()
    print("✅ Fire department creation completed!")
