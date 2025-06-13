#!/usr/bin/env python3
"""
Test script for login with email/username and location detection fixes
"""

from database import authenticate_user, get_user_by_username, get_user_by_email

def test_login_functionality():
    """Test login with both username and email"""
    print("🔐 Testing Login Functionality...")
    
    # Get test user
    user = get_user_by_username("testuser")
    if not user:
        print("❌ Test user not found. Please run create_test_data.py first.")
        return
    
    print(f"✅ Test user found: {user['username']} ({user['email']})")
    
    # Test login with username
    print("\n📝 Testing login with USERNAME...")
    auth_result = authenticate_user("testuser", "password123")
    if auth_result:
        print("✅ Login with username successful")
        print(f"   Authenticated user: {auth_result['full_name']}")
    else:
        print("❌ Login with username failed")
    
    # Test login with email
    print("\n📧 Testing login with EMAIL...")
    auth_result = authenticate_user("user@test.com", "password123")
    if auth_result:
        print("✅ Login with email successful")
        print(f"   Authenticated user: {auth_result['full_name']}")
    else:
        print("❌ Login with email failed")
    
    # Test wrong password
    print("\n🚫 Testing with WRONG PASSWORD...")
    auth_result = authenticate_user("testuser", "wrongpassword")
    if not auth_result:
        print("✅ Wrong password correctly rejected")
    else:
        print("❌ Wrong password was accepted (security issue!)")
    
    # Test non-existent user
    print("\n👻 Testing with NON-EXISTENT USER...")
    auth_result = authenticate_user("nonexistent@email.com", "password123")
    if not auth_result:
        print("✅ Non-existent user correctly rejected")
    else:
        print("❌ Non-existent user was accepted (security issue!)")

def test_database_functions():
    """Test database helper functions"""
    print("\n🗄️  Testing Database Functions...")
    
    # Test get_user_by_email
    user_by_email = get_user_by_email("user@test.com")
    if user_by_email:
        print("✅ get_user_by_email() working")
        print(f"   Found: {user_by_email['username']} - {user_by_email['full_name']}")
    else:
        print("❌ get_user_by_email() not working")
    
    # Test get_user_by_username
    user_by_username = get_user_by_username("testuser")
    if user_by_username:
        print("✅ get_user_by_username() working")
        print(f"   Found: {user_by_username['email']} - {user_by_username['full_name']}")
    else:
        print("❌ get_user_by_username() not working")

def test_fire_department_login():
    """Test fire department login"""
    print("\n🚒 Testing Fire Department Login...")
    
    # Test fire department login with username
    auth_result = authenticate_user("yaoundefire", "firepass123")
    if auth_result:
        print("✅ Fire department login with username successful")
        print(f"   Department: {auth_result['department_name']}")
        print(f"   User type: {auth_result['user_type']}")
    else:
        print("❌ Fire department login with username failed")
    
    # Test fire department login with email
    auth_result = authenticate_user("fire@yaounde.cm", "firepass123")
    if auth_result:
        print("✅ Fire department login with email successful")
        print(f"   Department: {auth_result['department_name']}")
        print(f"   User type: {auth_result['user_type']}")
    else:
        print("❌ Fire department login with email failed")

def print_location_testing_guide():
    """Print guide for testing location detection"""
    print("\n" + "="*60)
    print("📍 LOCATION DETECTION TESTING GUIDE")
    print("="*60)
    
    print("\n🌐 Browser Testing Steps:")
    print("1. Open http://127.0.0.1:3000 in your browser")
    print("2. Login with testuser / password123")
    print("3. Go to emergency reporting section")
    print("4. Observe automatic location detection on page load")
    print("5. Click 'Detect' button to manually refresh location")
    print("6. Check that location field is populated with address")
    
    print("\n🔧 What Should Happen:")
    print("• Page loads → Automatic location detection starts")
    print("• Browser asks for location permission → Allow it")
    print("• Location field automatically fills with your address")
    print("• Status shows: 'Location detected automatically (±Xm accuracy)'")
    print("• Click 'Detect' → Location refreshes with current position")
    
    print("\n⚠️  Troubleshooting:")
    print("• If location permission denied → Click 'Detect' to try again")
    print("• If no address shown → GPS coordinates will be used as fallback")
    print("• If timeout → Try clicking 'Detect' button manually")
    print("• Check browser console (F12) for detailed error messages")
    
    print("\n🌍 Location Services:")
    print("• Uses multiple geocoding services for reliability")
    print("• BigDataCloud API (primary)")
    print("• OpenStreetMap Nominatim (fallback)")
    print("• GPS coordinates (final fallback)")

def print_login_testing_guide():
    """Print guide for testing login functionality"""
    print("\n" + "="*60)
    print("🔐 LOGIN TESTING GUIDE")
    print("="*60)
    
    print("\n👤 Test Accounts (Username / Email / Password):")
    print("• Regular User:")
    print("  - Username: testuser")
    print("  - Email: user@test.com")
    print("  - Password: password123")
    
    print("\n🚒 Fire Department Accounts:")
    print("• Yaoundé Fire Department:")
    print("  - Username: yaoundefire")
    print("  - Email: fire@yaounde.cm")
    print("  - Password: firepass123")
    
    print("• Douala Fire Department:")
    print("  - Username: doualafire")
    print("  - Email: fire@douala.cm")
    print("  - Password: firepass123")
    
    print("\n🧪 Testing Steps:")
    print("1. Go to login page")
    print("2. Try logging in with USERNAME (e.g., 'testuser')")
    print("3. Try logging in with EMAIL (e.g., 'user@test.com')")
    print("4. Both should work with the same password")
    print("5. Test wrong password → Should be rejected")
    print("6. Test non-existent user → Should be rejected")

if __name__ == "__main__":
    print("🧪 TESTING LOGIN AND LOCATION FIXES")
    print("="*50)
    
    test_database_functions()
    test_login_functionality()
    test_fire_department_login()
    print_login_testing_guide()
    print_location_testing_guide()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED")
    print("="*60)
    print("🌐 Application running at: http://127.0.0.1:3000")
    print("📱 Ready for browser testing!")
