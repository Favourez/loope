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
        assert 'system_health' in data['data']
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
        assert 'emergency_id' in data['data']
    
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
        
        emergency_id = json.loads(create_response.data)['data']['emergency_id']
        
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
        assert 'title' in data['data']
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

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
