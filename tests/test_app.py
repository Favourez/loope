#!/usr/bin/env python3
"""
Unit tests for Emergency Response App
"""

import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import init_database

@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_database()
        yield client

@pytest.fixture
def api_headers():
    """API headers with authentication"""
    return {
        'Content-Type': 'application/json',
        'X-API-Key': 'emergency-api-key-2024'
    }

class TestHealthEndpoints:
    """Test health and status endpoints"""
    
    def test_health_endpoint(self, client):
        """Test health check endpoint"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert data['data']['status'] == 'healthy'
    
    def test_status_endpoint(self, client, api_headers):
        """Test system status endpoint"""
        response = client.get('/api/v1/status', headers=api_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'system_status' in data['data']
        assert 'active_users' in data['data']

class TestEmergencyEndpoints:
    """Test emergency-related endpoints"""
    
    def test_get_emergencies(self, client, api_headers):
        """Test getting all emergencies"""
        response = client.get('/api/v1/emergencies', headers=api_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'data' in data
    
    def test_create_emergency(self, client, api_headers):
        """Test creating emergency report"""
        emergency_data = {
            'emergency_type': 'fire',
            'location': 'Test Location',
            'description': 'Test emergency for unit testing',
            'severity': 'medium',
            'latitude': 3.8634,
            'longitude': 11.5167
        }
        
        response = client.post('/api/v1/emergencies', 
                              json=emergency_data,
                              headers=api_headers)
        assert response.status_code == 201
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'report_id' in data['data']
    
    def test_create_emergency_missing_data(self, client, api_headers):
        """Test creating emergency with missing required data"""
        emergency_data = {
            'emergency_type': 'fire'
            # Missing required fields
        }
        
        response = client.post('/api/v1/emergencies', 
                              json=emergency_data,
                              headers=api_headers)
        assert response.status_code == 400
    
    def test_update_emergency_status(self, client, api_headers):
        """Test updating emergency status"""
        # First create an emergency
        emergency_data = {
            'emergency_type': 'medical',
            'location': 'Test Hospital',
            'description': 'Test medical emergency',
            'severity': 'high'
        }
        
        create_response = client.post('/api/v1/emergencies', 
                                    json=emergency_data,
                                    headers=api_headers)
        assert create_response.status_code == 201
        
        emergency_id = json.loads(create_response.data)['data']['report_id']
        
        # Update status
        status_data = {'status': 'responding'}
        response = client.put(f'/api/v1/emergencies/{emergency_id}/status',
                             json=status_data,
                             headers=api_headers)
        assert response.status_code == 200

class TestFirstAidEndpoints:
    """Test first aid related endpoints"""
    
    def test_get_first_aid_practices(self, client, api_headers):
        """Test getting all first aid practices"""
        response = client.get('/api/v1/first-aid', headers=api_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']) > 0
    
    def test_get_specific_first_aid_practice(self, client, api_headers):
        """Test getting specific first aid practice"""
        response = client.get('/api/v1/first-aid/1', headers=api_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert 'name' in data['data']
        assert 'steps' in data['data']
    
    def test_get_nonexistent_first_aid_practice(self, client, api_headers):
        """Test getting non-existent first aid practice"""
        response = client.get('/api/v1/first-aid/999', headers=api_headers)
        assert response.status_code == 404

class TestFireDepartmentEndpoints:
    """Test fire department related endpoints"""
    
    def test_get_fire_departments(self, client, api_headers):
        """Test getting all fire departments"""
        response = client.get('/api/v1/fire-departments', headers=api_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
        assert len(data['data']) > 0

class TestMessagingEndpoints:
    """Test messaging system endpoints"""
    
    def test_get_messages(self, client, api_headers):
        """Test getting community messages"""
        response = client.get('/api/v1/messages', headers=api_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_create_message(self, client, api_headers):
        """Test creating community message"""
        message_data = {
            'content': 'Test community message',
            'message_type': 'info'
        }
        
        response = client.post('/api/v1/messages',
                              json=message_data,
                              headers=api_headers)
        assert response.status_code == 201

class TestAuthenticationEndpoints:
    """Test authentication related endpoints"""
    
    def test_login_valid_user(self, client):
        """Test login with valid credentials"""
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }
        
        response = client.post('/api/v1/auth/login',
                              json=login_data,
                              headers={'Content-Type': 'application/json'})
        
        # Should return 200 or 201 depending on implementation
        assert response.status_code in [200, 201]
    
    def test_login_invalid_user(self, client):
        """Test login with invalid credentials"""
        login_data = {
            'username': 'invaliduser',
            'password': 'wrongpassword'
        }
        
        response = client.post('/api/v1/auth/login',
                              json=login_data,
                              headers={'Content-Type': 'application/json'})
        assert response.status_code == 401

class TestAPIAuthentication:
    """Test API key authentication"""
    
    def test_endpoint_without_api_key(self, client):
        """Test accessing protected endpoint without API key"""
        response = client.get('/api/v1/emergencies')
        assert response.status_code == 401
    
    def test_endpoint_with_invalid_api_key(self, client):
        """Test accessing protected endpoint with invalid API key"""
        headers = {
            'Content-Type': 'application/json',
            'X-API-Key': 'invalid-key'
        }
        
        response = client.get('/api/v1/emergencies', headers=headers)
        assert response.status_code == 401
    
    def test_endpoint_with_valid_api_key(self, client, api_headers):
        """Test accessing protected endpoint with valid API key"""
        response = client.get('/api/v1/emergencies', headers=api_headers)
        assert response.status_code == 200

class TestErrorHandling:
    """Test error handling and edge cases"""
    
    def test_404_endpoint(self, client):
        """Test non-existent endpoint"""
        response = client.get('/api/v1/nonexistent')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client, api_headers):
        """Test method not allowed"""
        response = client.delete('/api/v1/health', headers=api_headers)
        assert response.status_code == 405
    
    def test_invalid_json(self, client, api_headers):
        """Test invalid JSON payload"""
        response = client.post('/api/v1/emergencies',
                              data='invalid json',
                              headers=api_headers)
        assert response.status_code == 400

    def test_missing_content_type(self, client):
        """Test request without content type"""
        headers = {'X-API-Key': 'emergency-api-key-2024'}
        response = client.post('/api/v1/emergencies',
                              json={'test': 'data'},
                              headers=headers)
        # Should still work or return appropriate error
        assert response.status_code in [200, 201, 400]

    def test_empty_request_body(self, client, api_headers):
        """Test empty request body"""
        response = client.post('/api/v1/emergencies',
                              json={},
                              headers=api_headers)
        assert response.status_code == 400

    def test_oversized_request(self, client, api_headers):
        """Test oversized request payload"""
        large_data = {
            'emergency_type': 'fire',
            'location': 'A' * 10000,  # Very large location string
            'description': 'B' * 10000,  # Very large description
            'severity': 'high'
        }
        response = client.post('/api/v1/emergencies',
                              json=large_data,
                              headers=api_headers)
        # Should handle gracefully
        assert response.status_code in [201, 400, 413]

    def test_sql_injection_attempt(self, client, api_headers):
        """Test SQL injection protection"""
        malicious_data = {
            'emergency_type': "fire'; DROP TABLE users; --",
            'location': 'Test Location',
            'description': 'Test description',
            'severity': 'high'
        }
        response = client.post('/api/v1/emergencies',
                              json=malicious_data,
                              headers=api_headers)
        # Should be rejected or sanitized
        assert response.status_code in [201, 400]

    def test_xss_attempt(self, client, api_headers):
        """Test XSS protection"""
        xss_data = {
            'emergency_type': 'fire',
            'location': '<script>alert("xss")</script>',
            'description': '<img src=x onerror=alert("xss")>',
            'severity': 'high'
        }
        response = client.post('/api/v1/emergencies',
                              json=xss_data,
                              headers=api_headers)
        # Should be sanitized or rejected
        assert response.status_code in [201, 400]

class TestMetricsEndpoint:
    """Test Prometheus metrics endpoint"""
    
    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert b'emergency_reports_total' in response.data
        assert b'system_health_score' in response.data

# Performance and Load Testing
class TestPerformance:
    """Test performance characteristics"""
    
    def test_health_endpoint_performance(self, client):
        """Test health endpoint response time"""
        import time
        
        start_time = time.time()
        response = client.get('/api/v1/health')
        end_time = time.time()
        
        assert response.status_code == 200
        assert (end_time - start_time) < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self, client, api_headers):
        """Test handling multiple concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get('/api/v1/health')
            results.append(response.status_code)
        
        # Create 10 concurrent threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 10

class TestWebRoutes:
    """Test web interface routes"""

    def test_index_route(self, client):
        """Test index page"""
        response = client.get('/')
        assert response.status_code == 200

    def test_login_page(self, client):
        """Test login page"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower()

    def test_register_page(self, client):
        """Test register page"""
        response = client.get('/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower()

    def test_first_aid_page(self, client):
        """Test first aid page"""
        response = client.get('/first_aid')
        assert response.status_code == 200

    def test_first_aid_detail_page(self, client):
        """Test first aid detail page"""
        response = client.get('/first_aid_detail/1')
        assert response.status_code == 200

    def test_map_page(self, client):
        """Test map page"""
        response = client.get('/map')
        assert response.status_code == 200

    def test_messages_page(self, client):
        """Test messages page"""
        response = client.get('/messages')
        assert response.status_code == 200

    def test_help_page(self, client):
        """Test help page"""
        response = client.get('/help')
        assert response.status_code == 200

    def test_profile_page_without_login(self, client):
        """Test profile page without login (should redirect)"""
        response = client.get('/profile')
        assert response.status_code in [302, 401]  # Redirect to login or unauthorized

class TestAdditionalAPIEndpoints:
    """Test additional API endpoints for better coverage"""

    def test_fire_departments_endpoint(self, client, api_headers):
        """Test fire departments endpoint"""
        response = client.get('/api/v1/fire-departments', headers=api_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'status' in data
        assert 'data' in data

    def test_hospitals_endpoint(self, client, api_headers):
        """Test hospitals endpoint"""
        response = client.get('/api/v1/hospitals', headers=api_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'status' in data
        assert 'data' in data

    def test_messages_api_endpoint(self, client, api_headers):
        """Test messages API endpoint"""
        response = client.get('/api/v1/messages', headers=api_headers)
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'status' in data
        assert 'data' in data

    def test_create_message_endpoint(self, client, api_headers):
        """Test create message endpoint"""
        message_data = {
            'content': 'Test community message',
            'message_type': 'info',
            'sender': 'Test User'
        }

        response = client.post('/api/v1/messages',
                              json=message_data,
                              headers=api_headers)
        assert response.status_code in [201, 200]

    def test_emergency_status_update(self, client, api_headers):
        """Test emergency status update"""
        # First create an emergency
        emergency_data = {
            'emergency_type': 'fire',
            'location': 'Test Location',
            'description': 'Test emergency',
            'severity': 'high',
            'latitude': 3.8634,
            'longitude': 11.5167,
            'reporter_name': 'Test User',
            'reporter_phone': '+237123456789'
        }

        create_response = client.post('/api/v1/emergencies',
                                    json=emergency_data,
                                    headers=api_headers)

        if create_response.status_code == 201:
            emergency_id = json.loads(create_response.data)['data']['report_id']

            # Update status
            status_data = {'status': 'responding'}
            update_response = client.put(f'/api/v1/emergencies/{emergency_id}/status',
                                       json=status_data,
                                       headers=api_headers)
            assert update_response.status_code in [200, 404]  # 404 if emergency not found

class TestInputValidation:
    """Test input validation and sanitization"""

    def test_emergency_type_validation(self, client, api_headers):
        """Test emergency type validation"""
        valid_types = ['fire', 'medical', 'accident', 'natural_disaster', 'security']

        for emergency_type in valid_types:
            data = {
                'emergency_type': emergency_type,
                'location': 'Test Location',
                'description': 'Test description',
                'severity': 'medium'
            }
            response = client.post('/api/v1/emergencies',
                                  json=data,
                                  headers=api_headers)
            assert response.status_code in [201, 400]  # Should be accepted or have validation error

    def test_severity_validation(self, client, api_headers):
        """Test severity validation"""
        valid_severities = ['low', 'medium', 'high', 'critical']

        for severity in valid_severities:
            data = {
                'emergency_type': 'fire',
                'location': 'Test Location',
                'description': 'Test description',
                'severity': severity
            }
            response = client.post('/api/v1/emergencies',
                                  json=data,
                                  headers=api_headers)
            assert response.status_code in [201, 400]

    def test_coordinate_validation(self, client, api_headers):
        """Test coordinate validation"""
        # Valid coordinates for Cameroon
        valid_coords = [
            (3.8634, 11.5167),  # Yaoundé
            (4.0511, 9.7679),   # Douala
            (5.9631, 10.1591)   # Garoua
        ]

        for lat, lng in valid_coords:
            data = {
                'emergency_type': 'fire',
                'location': 'Test Location',
                'description': 'Test description',
                'severity': 'medium',
                'latitude': lat,
                'longitude': lng
            }
            response = client.post('/api/v1/emergencies',
                                  json=data,
                                  headers=api_headers)
            assert response.status_code in [201, 400]

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
