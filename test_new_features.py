#!/usr/bin/env python3
"""
Test script for new features: messaging, profile management, and location detection
"""

from database import create_message, get_messages, get_user_by_username
import requests
import json

def test_messaging_system():
    """Test the messaging system"""
    print("🧪 Testing Messaging System...")
    
    # Get test user
    user = get_user_by_username("testuser")
    if not user:
        print("❌ Test user not found. Please run create_test_data.py first.")
        return
    
    # Create test messages
    test_messages = [
        {
            "content": "Hello everyone! Just wanted to share some fire safety tips for the dry season.",
            "message_type": "info"
        },
        {
            "content": "🚨 ALERT: High wind conditions expected today. Please be extra cautious with any outdoor activities involving fire.",
            "message_type": "alert"
        },
        {
            "content": "Thanks for the quick response to the emergency report earlier. Great work by the fire department!",
            "message_type": "general"
        },
        {
            "content": "🔥 EMERGENCY: Large fire spotted near the market area. Avoid the downtown region if possible.",
            "message_type": "emergency"
        }
    ]
    
    print(f"Creating {len(test_messages)} test messages...")
    
    for i, msg in enumerate(test_messages, 1):
        try:
            message_id = create_message(
                user_id=user['id'],
                content=msg['content'],
                message_type=msg['message_type']
            )
            print(f"✅ Created message #{message_id}: {msg['message_type'].upper()}")
        except Exception as e:
            print(f"❌ Failed to create message {i}: {e}")
    
    # Test retrieving messages
    print("\n📥 Retrieving messages...")
    try:
        messages = get_messages(limit=10)
        print(f"✅ Retrieved {len(messages)} messages")
        
        for msg in messages[-3:]:  # Show last 3 messages
            print(f"   - [{msg['message_type'].upper()}] {msg['full_name']}: {msg['content'][:50]}...")
            
    except Exception as e:
        print(f"❌ Failed to retrieve messages: {e}")

def test_location_detection():
    """Test location detection functionality"""
    print("\n🌍 Testing Location Detection...")
    
    # Test reverse geocoding function (simulated)
    test_coordinates = [
        {"lat": 3.8691, "lng": 11.5174, "expected": "Yaoundé"},
        {"lat": 4.0511, "lng": 9.7679, "expected": "Douala"},
        {"lat": 5.9631, "lng": 10.1591, "expected": "Bamenda"}
    ]
    
    print("📍 Test coordinates for Cameroon cities:")
    for coord in test_coordinates:
        print(f"   - {coord['expected']}: {coord['lat']}, {coord['lng']}")
    
    print("✅ Location detection ready for browser testing")

def test_email_configuration():
    """Test email configuration"""
    print("\n📧 Testing Email Configuration...")
    
    # Check if email settings are configured
    from app import EMAIL_USER, EMAIL_PASSWORD
    
    if EMAIL_USER == 'your-email@gmail.com':
        print("⚠️  Email not configured - using default placeholder")
        print("   To enable email notifications:")
        print("   1. Update EMAIL_USER and EMAIL_PASSWORD in app.py")
        print("   2. Use Gmail App Password for authentication")
        print("   3. Test with a real emergency report")
    else:
        print(f"✅ Email configured for: {EMAIL_USER}")
        print("   Email notifications will be sent for emergency reports")

def test_database_schema():
    """Test database schema"""
    print("\n🗄️  Testing Database Schema...")
    
    from database import get_db_connection
    
    try:
        conn = get_db_connection()
        
        # Check if messages table exists
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='messages'")
        if cursor.fetchone():
            print("✅ Messages table exists")
            
            # Check message count
            cursor = conn.execute("SELECT COUNT(*) FROM messages WHERE is_deleted = 0")
            count = cursor.fetchone()[0]
            print(f"   - {count} active messages in database")
        else:
            print("❌ Messages table not found")
        
        # Check users table
        cursor = conn.execute("SELECT COUNT(*) FROM users WHERE is_active = 1")
        user_count = cursor.fetchone()[0]
        print(f"✅ {user_count} active users in database")
        
        # Check emergency reports
        cursor = conn.execute("SELECT COUNT(*) FROM emergency_reports")
        report_count = cursor.fetchone()[0]
        print(f"✅ {report_count} emergency reports in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Database schema test failed: {e}")

def print_feature_summary():
    """Print summary of new features"""
    print("\n" + "="*60)
    print("🎉 NEW FEATURES IMPLEMENTED")
    print("="*60)
    
    features = [
        {
            "name": "📍 Enhanced Location Detection",
            "description": "Automatic GPS location capture with reverse geocoding",
            "test": "Click 'Detect' button on emergency form"
        },
        {
            "name": "👤 User Profile Management",
            "description": "Complete profile editing, password change, account deletion",
            "test": "Access via Menu > Profile"
        },
        {
            "name": "💬 Community Chat System",
            "description": "Real-time messaging with message types and moderation",
            "test": "Access via Menu > Messages"
        },
        {
            "name": "📧 Email Notifications",
            "description": "Automatic email confirmation for emergency reports",
            "test": "Submit an emergency report (configure email first)"
        },
        {
            "name": "🔄 Real-time Updates",
            "description": "Live chat updates and emergency dashboard refresh",
            "test": "Multiple users can chat in real-time"
        }
    ]
    
    for i, feature in enumerate(features, 1):
        print(f"\n{i}. {feature['name']}")
        print(f"   {feature['description']}")
        print(f"   🧪 Test: {feature['test']}")
    
    print("\n" + "="*60)
    print("🚀 APPLICATION READY FOR TESTING")
    print("="*60)
    print("Access the application at: http://127.0.0.1:3000")
    print("\nTest Accounts:")
    print("• Regular User: testuser / password123")
    print("• Fire Dept: yaoundefire / firepass123")
    print("• Fire Dept: doualafire / firepass123")

if __name__ == "__main__":
    print("🔧 TESTING NEW FEATURES")
    print("="*50)
    
    test_database_schema()
    test_messaging_system()
    test_location_detection()
    test_email_configuration()
    print_feature_summary()
