#!/usr/bin/env python3
"""
Integration tests for Emergency Response App
Tests the interaction between different modules and components
"""

import pytest
import sys
import os
import json
import time
import tempfile
import sqlite3
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import init_database, get_db_connection, create_user, create_emergency_report
from auth import hash_password, generate_api_key

@pytest.fixture
def test_app():
    """Create test application with isolated database"""
    app.config['TESTING'] = True
    app.config['DATABASE'] = ':memory:'
    
    with app.test_client() as client:
        with app.app_context():
            init_database()
            # Create test users
            create_user('testuser', 'password123', 'test@example.com', 'regular')
            create_user('fireuser', 'password123', 'fire@example.com', 'fire_department')
        yield client

@pytest.fixture
def api_headers():
    """API headers with authentication"""
    return {
        'Content-Type': 'application/json',
        'X-API-Key': 'emergency-api-key-2024'
    }

class TestUserAuthenticationFlow:
    """Test complete user authentication workflows"""
    
    def test_user_registration_and_login_flow(self, test_app):
        """Test complete user registration and login process"""
        # 1. Register new user
        registration_data = {
            'username': 'newuser',
            'password': 'NewUser123!',
            'email': 'newuser@example.com',
            'user_type': 'regular'
        }
        
        register_response = test_app.post('/register', 
                                        data=registration_data,
                                        follow_redirects=True)
        assert register_response.status_code == 200
        
        # 2. Login with new user
        login_data = {
            'username': 'newuser',
            'password': 'NewUser123!'
        }
        
        login_response = test_app.post('/login',
                                     data=login_data,
                                     follow_redirects=True)
        assert login_response.status_code == 200
        
        # 3. Access protected page
        profile_response = test_app.get('/profile')
        assert profile_response.status_code == 200
    
    def test_fire_department_user_flow(self, test_app):
        """Test fire department user specific workflow"""
        # Login as fire department user
        login_data = {
            'username': 'fireuser',
            'password': 'password123'
        }
        
        login_response = test_app.post('/login',
                                     data=login_data,
                                     follow_redirects=True)
        assert login_response.status_code == 200
        
        # Access fire department landing page
        fire_landing_response = test_app.get('/fire_department_landing')
        assert fire_landing_response.status_code == 200
        
        # Should have access to emergency dashboard
        assert b'Emergency Dashboard' in fire_landing_response.data or \
               b'emergency' in fire_landing_response.data.lower()

class TestEmergencyReportingFlow:
    """Test complete emergency reporting workflows"""
    
    def test_emergency_report_creation_and_retrieval(self, test_app, api_headers):
        """Test creating and retrieving emergency reports"""
        # 1. Create emergency report via API
        emergency_data = {
            'emergency_type': 'fire',
            'location': 'Downtown Yaoundé',
            'description': 'Large fire in commercial building',
            'severity': 'high',
            'latitude': 3.8634,
            'longitude': 11.5167,
            'reporter_name': 'John Doe',
            'reporter_phone': '+237123456789'
        }
        
        create_response = test_app.post('/api/v1/emergencies',
                                      json=emergency_data,
                                      headers=api_headers)
        assert create_response.status_code == 201
        
        response_data = json.loads(create_response.data)
        emergency_id = response_data['data']['emergency_id']
        
        # 2. Retrieve emergency reports
        get_response = test_app.get('/api/v1/emergencies', headers=api_headers)
        assert get_response.status_code == 200
        
        reports_data = json.loads(get_response.data)
        assert len(reports_data['data']) > 0
        
        # 3. Find our created emergency
        created_emergency = None
        for report in reports_data['data']:
            if report['id'] == emergency_id:
                created_emergency = report
                break
        
        assert created_emergency is not None
        assert created_emergency['emergency_type'] == 'fire'
        assert created_emergency['location'] == 'Downtown Yaoundé'
        
        # 4. Update emergency status
        status_update = {'status': 'responding'}
        update_response = test_app.put(f'/api/v1/emergencies/{emergency_id}/status',
                                     json=status_update,
                                     headers=api_headers)
        assert update_response.status_code == 200
    
    def test_emergency_report_validation(self, test_app, api_headers):
        """Test emergency report validation and error handling"""
        # Test with missing required fields
        incomplete_data = {
            'emergency_type': 'medical'
            # Missing location, description, etc.
        }
        
        response = test_app.post('/api/v1/emergencies',
                               json=incomplete_data,
                               headers=api_headers)
        assert response.status_code == 400
        
        # Test with invalid emergency type
        invalid_data = {
            'emergency_type': 'invalid_type',
            'location': 'Test Location',
            'description': 'Test description',
            'severity': 'medium'
        }
        
        response = test_app.post('/api/v1/emergencies',
                               json=invalid_data,
                               headers=api_headers)
        assert response.status_code == 400

class TestMessagingSystemFlow:
    """Test messaging system integration"""
    
    def test_message_creation_and_retrieval(self, test_app, api_headers):
        """Test creating and retrieving community messages"""
        # 1. Create message
        message_data = {
            'content': 'Emergency drill scheduled for tomorrow at 10 AM',
            'message_type': 'announcement',
            'sender': 'Fire Department'
        }
        
        create_response = test_app.post('/api/v1/messages',
                                      json=message_data,
                                      headers=api_headers)
        assert create_response.status_code == 201
        
        # 2. Retrieve messages
        get_response = test_app.get('/api/v1/messages', headers=api_headers)
        assert get_response.status_code == 200
        
        messages_data = json.loads(get_response.data)
        assert len(messages_data['data']) > 0
        
        # 3. Verify our message exists
        found_message = False
        for message in messages_data['data']:
            if message['content'] == message_data['content']:
                found_message = True
                break
        
        assert found_message is True
    
    def test_message_web_interface(self, test_app):
        """Test message display in web interface"""
        # Login first
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }
        
        test_app.post('/login', data=login_data, follow_redirects=True)
        
        # Access messages page
        messages_response = test_app.get('/messages')
        assert messages_response.status_code == 200
        assert b'messages' in messages_response.data.lower()

class TestFirstAidSystemFlow:
    """Test first aid system integration"""
    
    def test_first_aid_practices_retrieval(self, test_app, api_headers):
        """Test retrieving first aid practices"""
        # Get all practices
        response = test_app.get('/api/v1/first-aid', headers=api_headers)
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert len(data['data']) > 0
        
        # Get specific practice
        practice_id = data['data'][0]['id']
        specific_response = test_app.get(f'/api/v1/first-aid/{practice_id}', 
                                       headers=api_headers)
        assert specific_response.status_code == 200
        
        specific_data = json.loads(specific_response.data)
        assert 'title' in specific_data['data']
        assert 'steps' in specific_data['data']
    
    def test_first_aid_web_interface(self, test_app):
        """Test first aid web interface"""
        # Access first aid page
        response = test_app.get('/first_aid')
        assert response.status_code == 200
        assert b'first aid' in response.data.lower() or b'first-aid' in response.data.lower()
        
        # Access specific first aid detail
        detail_response = test_app.get('/first_aid_detail/1')
        assert detail_response.status_code == 200

class TestAPIAuthenticationFlow:
    """Test API authentication and authorization"""
    
    def test_api_key_authentication(self, test_app):
        """Test API key authentication flow"""
        # Test without API key
        response = test_app.get('/api/v1/emergencies')
        assert response.status_code == 401
        
        # Test with invalid API key
        invalid_headers = {
            'Content-Type': 'application/json',
            'X-API-Key': 'invalid-key'
        }
        response = test_app.get('/api/v1/emergencies', headers=invalid_headers)
        assert response.status_code == 401
        
        # Test with valid API key
        valid_headers = {
            'Content-Type': 'application/json',
            'X-API-Key': 'emergency-api-key-2024'
        }
        response = test_app.get('/api/v1/emergencies', headers=valid_headers)
        assert response.status_code == 200
    
    def test_session_based_authentication(self, test_app):
        """Test session-based authentication for web interface"""
        # Access protected page without login
        response = test_app.get('/profile')
        assert response.status_code == 302  # Redirect to login
        
        # Login
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }
        
        login_response = test_app.post('/login',
                                     data=login_data,
                                     follow_redirects=True)
        assert login_response.status_code == 200
        
        # Now access protected page
        profile_response = test_app.get('/profile')
        assert profile_response.status_code == 200

class TestDatabaseIntegration:
    """Test database integration across modules"""
    
    def test_database_consistency(self, test_app, api_headers):
        """Test database consistency across operations"""
        # Create emergency via API
        emergency_data = {
            'emergency_type': 'medical',
            'location': 'Central Hospital',
            'description': 'Medical emergency',
            'severity': 'high',
            'latitude': 3.8634,
            'longitude': 11.5167,
            'reporter_name': 'Jane Doe',
            'reporter_phone': '+237987654321'
        }
        
        create_response = test_app.post('/api/v1/emergencies',
                                      json=emergency_data,
                                      headers=api_headers)
        assert create_response.status_code == 201
        
        emergency_id = json.loads(create_response.data)['data']['emergency_id']
        
        # Verify in database directly
        with app.app_context():
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM emergency_reports WHERE id = ?", (emergency_id,))
                db_emergency = cursor.fetchone()
                conn.close()
                
                assert db_emergency is not None
                assert db_emergency[1] == 'medical'  # emergency_type
                assert db_emergency[2] == 'Central Hospital'  # location
    
    def test_concurrent_database_operations(self, test_app, api_headers):
        """Test concurrent database operations"""
        import threading
        import time
        
        results = []
        
        def create_emergency(emergency_type):
            emergency_data = {
                'emergency_type': emergency_type,
                'location': f'Location for {emergency_type}',
                'description': f'Emergency of type {emergency_type}',
                'severity': 'medium',
                'latitude': 3.8634,
                'longitude': 11.5167,
                'reporter_name': 'Test User',
                'reporter_phone': '+237123456789'
            }
            
            response = test_app.post('/api/v1/emergencies',
                                   json=emergency_data,
                                   headers=api_headers)
            results.append(response.status_code)
        
        # Create multiple emergencies concurrently
        threads = []
        emergency_types = ['fire', 'medical', 'accident', 'natural_disaster']
        
        for emergency_type in emergency_types:
            thread = threading.Thread(target=create_emergency, args=(emergency_type,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All operations should succeed
        assert all(status == 201 for status in results)
        assert len(results) == len(emergency_types)

class TestSystemHealthFlow:
    """Test system health and monitoring integration"""
    
    def test_health_check_flow(self, test_app):
        """Test complete health check flow"""
        # Test health endpoint
        health_response = test_app.get('/api/v1/health')
        assert health_response.status_code == 200
        
        health_data = json.loads(health_response.data)
        assert health_data['status'] == 'success'
        assert health_data['data']['status'] == 'healthy'
        
        # Test metrics endpoint
        metrics_response = test_app.get('/metrics')
        assert metrics_response.status_code == 200
        assert b'emergency_reports_total' in metrics_response.data
    
    def test_system_status_monitoring(self, test_app, api_headers):
        """Test system status monitoring"""
        # Get system status
        status_response = test_app.get('/api/v1/status', headers=api_headers)
        assert status_response.status_code == 200
        
        status_data = json.loads(status_response.data)
        assert 'system_health' in status_data['data']
        assert 'active_users' in status_data['data']
        assert 'database_status' in status_data['data']

class TestErrorHandlingIntegration:
    """Test error handling across the system"""
    
    def test_database_error_handling(self, test_app, api_headers):
        """Test error handling when database is unavailable"""
        # Mock database connection failure
        with patch('database.get_db_connection', return_value=None):
            response = test_app.get('/api/v1/emergencies', headers=api_headers)
            assert response.status_code == 500
    
    def test_invalid_data_handling(self, test_app, api_headers):
        """Test handling of invalid data across endpoints"""
        # Test invalid JSON
        response = test_app.post('/api/v1/emergencies',
                               data='invalid json',
                               headers=api_headers)
        assert response.status_code == 400
        
        # Test missing content type
        headers_no_content_type = {'X-API-Key': 'emergency-api-key-2024'}
        response = test_app.post('/api/v1/emergencies',
                               json={'test': 'data'},
                               headers=headers_no_content_type)
        # Should still work or return appropriate error

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
