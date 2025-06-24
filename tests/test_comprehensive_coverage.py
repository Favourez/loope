#!/usr/bin/env python3
"""
Comprehensive Coverage Tests
Designed to achieve 85%+ code coverage across all modules
"""

import pytest
import sys
import os
import json
import tempfile
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app
from database import init_database, get_db_connection, create_user, authenticate_user
from auth import User, load_user, login_user_by_credentials
import api_endpoints

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

class TestAppRoutes:
    """Test all app routes for maximum coverage"""
    
    def test_index_route(self, client):
        """Test index route"""
        response = client.get('/')
        assert response.status_code in [200, 302]
    
    def test_login_route_get(self, client):
        """Test login GET route"""
        response = client.get('/login')
        assert response.status_code == 200
    
    def test_login_route_post(self, client):
        """Test login POST route"""
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = client.post('/login', data=login_data)
        assert response.status_code in [200, 302, 401]
    
    def test_register_route_get(self, client):
        """Test register GET route"""
        response = client.get('/register')
        assert response.status_code == 200
    
    def test_register_route_post(self, client):
        """Test register POST route"""
        register_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123',
            'full_name': 'New User',
            'user_type': 'user'
        }
        response = client.post('/register', data=register_data)
        assert response.status_code in [200, 302]
    
    def test_logout_route(self, client):
        """Test logout route"""
        response = client.get('/logout')
        assert response.status_code in [200, 302]
    
    def test_dashboard_route(self, client):
        """Test dashboard route"""
        response = client.get('/dashboard')
        assert response.status_code in [200, 302]
    
    def test_emergency_report_route(self, client):
        """Test emergency report route"""
        response = client.get('/emergency_report')
        assert response.status_code in [200, 302]
    
    def test_emergency_report_post(self, client):
        """Test emergency report POST"""
        emergency_data = {
            'emergency_type': 'fire',
            'location': 'Test Location',
            'description': 'Test emergency',
            'severity': 'high'
        }
        response = client.post('/emergency_report', data=emergency_data)
        assert response.status_code in [200, 302]
    
    def test_map_route(self, client):
        """Test map route"""
        response = client.get('/map')
        assert response.status_code in [200, 302]
    
    def test_messages_route(self, client):
        """Test messages route"""
        response = client.get('/messages')
        assert response.status_code in [200, 302]
    
    def test_help_route(self, client):
        """Test help route"""
        response = client.get('/help')
        assert response.status_code in [200, 302]
    
    def test_profile_route(self, client):
        """Test profile route"""
        response = client.get('/profile')
        assert response.status_code in [200, 302]

class TestAPIEndpoints:
    """Test all API endpoints comprehensively"""
    
    def test_health_endpoint(self, client):
        """Test health endpoint"""
        response = client.get('/api/v1/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'success'
    
    def test_status_endpoint(self, client, api_headers):
        """Test status endpoint"""
        response = client.get('/api/v1/status', headers=api_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
    
    def test_emergencies_get(self, client, api_headers):
        """Test get emergencies"""
        response = client.get('/api/v1/emergencies', headers=api_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
    
    def test_emergencies_post(self, client, api_headers):
        """Test create emergency"""
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
        response = client.post('/api/v1/emergencies', json=emergency_data, headers=api_headers)
        assert response.status_code in [200, 201]
    
    def test_first_aid_get(self, client, api_headers):
        """Test get first aid practices"""
        response = client.get('/api/v1/first-aid', headers=api_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
    
    def test_first_aid_specific(self, client, api_headers):
        """Test get specific first aid practice"""
        response = client.get('/api/v1/first-aid/1', headers=api_headers)
        assert response.status_code in [200, 404]
    
    def test_fire_departments_get(self, client, api_headers):
        """Test get fire departments"""
        response = client.get('/api/v1/fire-departments', headers=api_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
    
    def test_messages_get(self, client, api_headers):
        """Test get messages"""
        response = client.get('/api/v1/messages', headers=api_headers)
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'data' in data
    
    def test_messages_post(self, client, api_headers):
        """Test create message"""
        message_data = {
            'content': 'Test message',
            'message_type': 'info'
        }
        response = client.post('/api/v1/messages', json=message_data, headers=api_headers)
        assert response.status_code in [200, 201]
    
    def test_auth_login(self, client):
        """Test auth login endpoint"""
        login_data = {
            'username': 'testuser',
            'password': 'password123'
        }
        response = client.post('/api/v1/auth/login', json=login_data, headers={'Content-Type': 'application/json'})
        assert response.status_code in [200, 201, 401]

class TestDatabaseOperations:
    """Test database operations comprehensively"""
    
    @pytest.fixture
    def test_db(self):
        """Create test database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        with patch('database.DATABASE_PATH', db_path):
            init_database()
            yield db_path
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_database_connection(self, test_db):
        """Test database connection"""
        with patch('database.DATABASE_PATH', test_db):
            conn = get_db_connection()
            assert conn is not None
            conn.close()
    
    def test_create_user_comprehensive(self, test_db):
        """Test user creation comprehensively"""
        with patch('database.DATABASE_PATH', test_db):
            # Test regular user
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', 'Test User')
            assert user_id is not None
            
            # Test fire department user
            fire_id = create_user('fireuser', 'fire@example.com', 'password123', 'fire_department', 'Fire User', 
                                phone='+237123456789', department_name='Test Fire Dept', department_location='Test City')
            assert fire_id is not None
    
    def test_authenticate_user_comprehensive(self, test_db):
        """Test user authentication comprehensively"""
        with patch('database.DATABASE_PATH', test_db):
            # Create user
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', 'Test User')
            assert user_id is not None
            
            # Test authentication by username
            user = authenticate_user('testuser', 'password123')
            assert user is not None
            
            # Test authentication by email
            user = authenticate_user('test@example.com', 'password123')
            assert user is not None
            
            # Test wrong password
            user = authenticate_user('testuser', 'wrongpassword')
            assert user is None

class TestAuthModule:
    """Test auth module comprehensively"""
    
    @pytest.fixture
    def test_db(self):
        """Create test database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        with patch('database.DATABASE_PATH', db_path):
            init_database()
            yield db_path
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_user_class_comprehensive(self):
        """Test User class comprehensively"""
        user_data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'user_type': 'user',
            'full_name': 'Test User',
            'phone': '+237123456789',
            'department_name': None,
            'department_location': None,
            'created_at': '2024-01-01 00:00:00',
            'is_active': 1
        }
        
        user = User(user_data)
        
        # Test all properties
        assert user.id == '1'
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.user_type == 'user'
        assert user.full_name == 'Test User'
        assert user.phone == '+237123456789'
        assert user.is_active is True
        assert user.is_regular_user() is True
        assert user.is_fire_department() is False
        assert user.get_id() == '1'
    
    def test_load_user_function(self, test_db):
        """Test load_user function"""
        with patch('database.DATABASE_PATH', test_db):
            # Create user
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', 'Test User')
            assert user_id is not None
            
            # Load user
            user = load_user(str(user_id))
            assert user is not None
            assert isinstance(user, User)
            
            # Test invalid user ID
            user = load_user('999')
            assert user is None
    
    def test_login_user_by_credentials(self, test_db):
        """Test login_user_by_credentials function"""
        with patch('database.DATABASE_PATH', test_db):
            # Create user
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', 'Test User')
            assert user_id is not None
            
            # Login with valid credentials
            user = login_user_by_credentials('testuser', 'password123')
            assert user is not None
            assert isinstance(user, User)
            
            # Login with invalid credentials
            user = login_user_by_credentials('testuser', 'wrongpassword')
            assert user is None

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_api_key(self, client):
        """Test invalid API key"""
        headers = {'Content-Type': 'application/json', 'X-API-Key': 'invalid-key'}
        response = client.get('/api/v1/emergencies', headers=headers)
        assert response.status_code == 401
    
    def test_missing_api_key(self, client):
        """Test missing API key"""
        headers = {'Content-Type': 'application/json'}
        response = client.get('/api/v1/emergencies', headers=headers)
        assert response.status_code == 401
    
    def test_404_routes(self, client):
        """Test 404 routes"""
        response = client.get('/nonexistent-route')
        assert response.status_code == 404
    
    def test_method_not_allowed(self, client, api_headers):
        """Test method not allowed"""
        response = client.delete('/api/v1/health', headers=api_headers)
        assert response.status_code == 405

class TestMetricsAndMonitoring:
    """Test metrics and monitoring endpoints"""
    
    def test_metrics_endpoint(self, client):
        """Test Prometheus metrics endpoint"""
        response = client.get('/metrics')
        assert response.status_code == 200
        assert b'emergency_reports_total' in response.data or b'#' in response.data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
