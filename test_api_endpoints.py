#!/usr/bin/env python3
"""
Emergency Response App - API Endpoint Testing Script
Tests all API endpoints with various scenarios
"""

import requests
import json
import time
import sys
from datetime import datetime

# Configuration
BASE_URL = "http://127.0.0.1:3000/api/v1"
API_KEY = "emergency-api-key-2024"
HEADERS = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

class APITester:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.results = []

    def test_endpoint(self, name, method, endpoint, data=None, expected_status=200, headers=None):
        """Test a single API endpoint"""
        print(f"\n🧪 Testing: {name}")
        print(f"   {method} {endpoint}")
        
        try:
            url = f"{BASE_URL}{endpoint}"
            test_headers = headers or HEADERS
            
            if method.upper() == "GET":
                response = requests.get(url, headers=test_headers)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, headers=test_headers)
            elif method.upper() == "PUT":
                response = requests.put(url, json=data, headers=test_headers)
            elif method.upper() == "DELETE":
                response = requests.delete(url, headers=test_headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            # Check status code
            if response.status_code == expected_status:
                print(f"   ✅ Status: {response.status_code} (Expected: {expected_status})")
                self.passed += 1
                result = "PASS"
            else:
                print(f"   ❌ Status: {response.status_code} (Expected: {expected_status})")
                self.failed += 1
                result = "FAIL"
            
            # Print response
            try:
                response_json = response.json()
                print(f"   📄 Response: {json.dumps(response_json, indent=2)[:200]}...")
            except:
                print(f"   📄 Response: {response.text[:200]}...")
            
            self.results.append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "status_code": response.status_code,
                "expected_status": expected_status,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })
            
            return response
            
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
            self.failed += 1
            self.results.append({
                "name": name,
                "method": method,
                "endpoint": endpoint,
                "error": str(e),
                "result": "ERROR",
                "timestamp": datetime.now().isoformat()
            })
            return None

    def run_all_tests(self):
        """Run comprehensive API tests"""
        print("🚀 Starting Emergency Response App API Tests")
        print("=" * 60)
        
        # Test 1: Health Check (No API key required)
        self.test_endpoint(
            "Health Check",
            "GET",
            "/health",
            headers={"Content-Type": "application/json"}
        )
        
        # Test 2: System Status
        self.test_endpoint(
            "System Status",
            "GET",
            "/status"
        )
        
        # Test 3: Authentication - Login
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        login_response = self.test_endpoint(
            "User Login",
            "POST",
            "/auth/login",
            data=login_data,
            headers={"Content-Type": "application/json"}
        )
        
        # Test 4: Authentication - Register
        register_data = {
            "username": f"testuser_{int(time.time())}",
            "email": f"test_{int(time.time())}@example.com",
            "password": "password123",
            "full_name": "Test User",
            "phone": "+237123456789",
            "user_type": "regular"
        }
        self.test_endpoint(
            "User Registration",
            "POST",
            "/auth/register",
            data=register_data,
            expected_status=201,
            headers={"Content-Type": "application/json"}
        )
        
        # Test 5: Get All Emergencies
        self.test_endpoint(
            "Get All Emergencies",
            "GET",
            "/emergencies"
        )
        
        # Test 6: Get Emergencies with Filters
        self.test_endpoint(
            "Get Filtered Emergencies",
            "GET",
            "/emergencies?status=pending&limit=5"
        )
        
        # Test 7: Create Emergency Report
        emergency_data = {
            "emergency_type": "fire",
            "location": "Test Location - API Test",
            "description": "API test emergency report",
            "severity": "medium",
            "latitude": 3.8634,
            "longitude": 11.5167,
            "user_id": 1
        }
        emergency_response = self.test_endpoint(
            "Create Emergency Report",
            "POST",
            "/emergencies",
            data=emergency_data,
            expected_status=201
        )
        
        # Test 8: Get Specific Emergency (if creation was successful)
        if emergency_response and emergency_response.status_code == 201:
            try:
                report_id = emergency_response.json()["data"]["report_id"]
                self.test_endpoint(
                    "Get Specific Emergency",
                    "GET",
                    f"/emergencies/{report_id}"
                )
                
                # Test 9: Update Emergency Status
                status_data = {"status": "responding"}
                self.test_endpoint(
                    "Update Emergency Status",
                    "PUT",
                    f"/emergencies/{report_id}/status",
                    data=status_data
                )
            except:
                print("   ⚠️  Skipping specific emergency tests (creation failed)")
        
        # Test 10: Get Fire Departments
        self.test_endpoint(
            "Get Fire Departments",
            "GET",
            "/fire-departments"
        )
        
        # Test 11: Get Messages
        self.test_endpoint(
            "Get Community Messages",
            "GET",
            "/messages"
        )
        
        # Test 12: Create Message
        message_data = {
            "content": f"API test message - {datetime.now().isoformat()}",
            "message_type": "general",
            "user_id": 1
        }
        message_response = self.test_endpoint(
            "Create Community Message",
            "POST",
            "/messages",
            data=message_data,
            expected_status=201
        )
        
        # Test 13: Get First Aid Practices
        self.test_endpoint(
            "Get First Aid Practices",
            "GET",
            "/first-aid"
        )
        
        # Test 14: Get Filtered First Aid Practices
        self.test_endpoint(
            "Get Filtered First Aid",
            "GET",
            "/first-aid?category=Cardiac Emergency&difficulty=Intermediate"
        )
        
        # Test 15: Get Specific First Aid Practice
        self.test_endpoint(
            "Get Specific First Aid Practice",
            "GET",
            "/first-aid/1"
        )
        
        # Test 16: Invalid API Key
        self.test_endpoint(
            "Invalid API Key Test",
            "GET",
            "/emergencies",
            headers={"X-API-Key": "invalid-key"},
            expected_status=401
        )
        
        # Test 17: Missing API Key
        self.test_endpoint(
            "Missing API Key Test",
            "GET",
            "/emergencies",
            headers={"Content-Type": "application/json"},
            expected_status=401
        )
        
        # Test 18: Invalid Endpoint
        self.test_endpoint(
            "Invalid Endpoint Test",
            "GET",
            "/nonexistent",
            expected_status=404
        )

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"📈 Success Rate: {(self.passed / (self.passed + self.failed) * 100):.1f}%")
        
        if self.failed > 0:
            print("\n❌ Failed Tests:")
            for result in self.results:
                if result["result"] in ["FAIL", "ERROR"]:
                    print(f"   - {result['name']}: {result.get('error', 'Status code mismatch')}")
        
        # Save results to file
        with open(f"api_test_results_{int(time.time())}.json", "w") as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n📄 Detailed results saved to: api_test_results_{int(time.time())}.json")

def main():
    """Main function"""
    print("🔧 Emergency Response App API Testing Tool")
    print("=" * 60)
    
    # Check if app is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ App is running (Status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        print(f"❌ App is not accessible: {e}")
        print("Please make sure the Emergency Response App is running on http://127.0.0.1:3000")
        sys.exit(1)
    
    # Run tests
    tester = APITester()
    tester.run_all_tests()
    tester.print_summary()
    
    # Exit with appropriate code
    sys.exit(0 if tester.failed == 0 else 1)

if __name__ == "__main__":
    main()
