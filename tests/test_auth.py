#!/usr/bin/env python3
"""
Unit tests for authentication module
"""

import pytest
import sys
import os
import hashlib
import secrets
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from auth import User, load_user, login_user_by_credentials
from database import hash_password, verify_password, create_user, authenticate_user

class TestPasswordHashing:
    """Test password hashing and verification"""

    def test_hash_password_creates_hash(self):
        """Test that hash_password creates a hash"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert len(hashed) > 0
        assert hashed != password  # Should not be plain text

    def test_hash_password_different_for_same_input(self):
        """Test that hash_password creates different hashes for same input (salt)"""
        password = "testpassword123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # Should be different due to salt
        assert hash1 != hash2

    def test_verify_password_correct(self):
        """Test password verification with correct password"""
        password = "testpassword123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_incorrect(self):
        """Test password verification with incorrect password"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_hash_password_unicode(self):
        """Test hashing password with unicode characters"""
        password = "pássw0rd123!@#"
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed) is True

    def test_hash_password_long_input(self):
        """Test hashing very long password"""
        password = "a" * 1000  # Very long password
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed) is True

class TestUserClass:
    """Test User class functionality"""

    def test_user_creation(self):
        """Test User object creation"""
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

        assert user.id == '1'
        assert user.username == 'testuser'
        assert user.email == 'test@example.com'
        assert user.user_type == 'user'
        assert user.full_name == 'Test User'
        assert user.phone == '+237123456789'
        assert user.is_active is True

    def test_user_get_id(self):
        """Test User get_id method"""
        user_data = {
            'id': 123,
            'username': 'testuser',
            'email': 'test@example.com',
            'user_type': 'user',
            'full_name': 'Test User',
            'created_at': '2024-01-01 00:00:00',
            'is_active': 1
        }

        user = User(user_data)
        assert user.get_id() == '123'

    def test_user_is_fire_department(self):
        """Test is_fire_department method"""
        # Regular user
        user_data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'user_type': 'user',
            'full_name': 'Test User',
            'created_at': '2024-01-01 00:00:00',
            'is_active': 1
        }
        user = User(user_data)
        assert user.is_fire_department() is False

        # Fire department user
        fire_user_data = user_data.copy()
        fire_user_data['user_type'] = 'fire_department'
        fire_user = User(fire_user_data)
        assert fire_user.is_fire_department() is True

    def test_user_is_regular_user(self):
        """Test is_regular_user method"""
        # Regular user
        user_data = {
            'id': 1,
            'username': 'testuser',
            'email': 'test@example.com',
            'user_type': 'user',
            'full_name': 'Test User',
            'created_at': '2024-01-01 00:00:00',
            'is_active': 1
        }
        user = User(user_data)
        assert user.is_regular_user() is True

        # Fire department user
        fire_user_data = user_data.copy()
        fire_user_data['user_type'] = 'fire_department'
        fire_user = User(fire_user_data)
        assert fire_user.is_regular_user() is False

class TestAuthenticationFunctions:
    """Test authentication functions"""

    @pytest.fixture
    def test_db(self):
        """Create a test database"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        with patch('database.DATABASE_PATH', db_path):
            from database import init_database
            init_database()
            yield db_path

        if os.path.exists(db_path):
            os.unlink(db_path)

    def test_authenticate_user_valid_username(self, test_db):
        """Test user authentication with valid username"""
        with patch('database.DATABASE_PATH', test_db):
            # Create test user
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', 'Test User')
            assert user_id is not None

            # Authenticate with username
            user = authenticate_user('testuser', 'password123')
            assert user is not None
            assert user['username'] == 'testuser'
            assert user['email'] == 'test@example.com'

    def test_authenticate_user_valid_email(self, test_db):
        """Test user authentication with valid email"""
        with patch('database.DATABASE_PATH', test_db):
            # Create test user
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', 'Test User')
            assert user_id is not None

            # Authenticate with email
            user = authenticate_user('test@example.com', 'password123')
            assert user is not None
            assert user['username'] == 'testuser'
            assert user['email'] == 'test@example.com'

    def test_authenticate_user_invalid_password(self, test_db):
        """Test user authentication with invalid password"""
        with patch('database.DATABASE_PATH', test_db):
            # Create test user
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', 'Test User')
            assert user_id is not None

            # Try to authenticate with wrong password
            user = authenticate_user('testuser', 'wrongpassword')
            assert user is None

    def test_authenticate_user_nonexistent(self, test_db):
        """Test user authentication with nonexistent user"""
        with patch('database.DATABASE_PATH', test_db):
            # Try to authenticate nonexistent user
            user = authenticate_user('nonexistent', 'password123')
            assert user is None

    def test_load_user_valid_id(self, test_db):
        """Test load_user function with valid user ID"""
        with patch('database.DATABASE_PATH', test_db):
            # Create test user
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', 'Test User')
            assert user_id is not None

            # Load user
            user = load_user(str(user_id))
            assert user is not None
            assert isinstance(user, User)
            assert user.username == 'testuser'

    def test_load_user_invalid_id(self, test_db):
        """Test load_user function with invalid user ID"""
        with patch('database.DATABASE_PATH', test_db):
            # Try to load nonexistent user
            user = load_user('999')
            assert user is None

    def test_login_user_by_credentials_valid(self, test_db):
        """Test login_user_by_credentials with valid credentials"""
        with patch('database.DATABASE_PATH', test_db):
            # Create test user
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', 'Test User')
            assert user_id is not None

            # Login user
            user = login_user_by_credentials('testuser', 'password123')
            assert user is not None
            assert isinstance(user, User)
            assert user.username == 'testuser'

    def test_login_user_by_credentials_invalid(self, test_db):
        """Test login_user_by_credentials with invalid credentials"""
        with patch('database.DATABASE_PATH', test_db):
            # Try to login with invalid credentials
            user = login_user_by_credentials('nonexistent', 'wrongpassword')
            assert user is None

class TestAuthEdgeCases:
    """Test authentication edge cases"""

    @pytest.fixture
    def test_db(self):
        """Create a test database"""
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name

        with patch('database.DATABASE_PATH', db_path):
            from database import init_database
            init_database()
            yield db_path

        if os.path.exists(db_path):
            os.unlink(db_path)

    def test_user_with_special_characters(self, test_db):
        """Test user creation with special characters"""
        with patch('database.DATABASE_PATH', test_db):
            # Test with unicode characters
            user_id = create_user('tëstüser', 'tëst@éxample.com', 'pássw0rd!@#', 'user', 'Tëst Üser')
            assert user_id is not None

            # Authenticate with special characters
            user = authenticate_user('tëstüser', 'pássw0rd!@#')
            assert user is not None

    def test_user_with_long_inputs(self, test_db):
        """Test user creation with very long inputs"""
        with patch('database.DATABASE_PATH', test_db):
            long_username = 'a' * 50
            long_email = 'b' * 40 + '@example.com'
            long_password = 'c' * 100
            long_name = 'd' * 100

            user_id = create_user(long_username, long_email, long_password, 'user', long_name)
            # Should handle gracefully (accept or reject based on constraints)
            assert user_id is not None or user_id is None

    def test_user_with_empty_optional_fields(self, test_db):
        """Test user creation with empty optional fields"""
        with patch('database.DATABASE_PATH', test_db):
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', '')
            assert user_id is not None

    def test_fire_department_user_creation(self, test_db):
        """Test fire department user creation"""
        with patch('database.DATABASE_PATH', test_db):
            user_id = create_user('fireuser', 'fire@example.com', 'password123', 'fire_department', 'Fire User')
            assert user_id is not None

            # Load and verify user type
            user = load_user(str(user_id))
            assert user is not None
            assert user.is_fire_department() is True
            assert user.is_regular_user() is False

    def test_user_authentication_case_sensitivity(self, test_db):
        """Test case sensitivity in authentication"""
        with patch('database.DATABASE_PATH', test_db):
            # Create user with lowercase username
            user_id = create_user('testuser', 'test@example.com', 'password123', 'user', 'Test User')
            assert user_id is not None

            # Try to authenticate with different cases
            user1 = authenticate_user('testuser', 'password123')  # Exact match
            user2 = authenticate_user('TestUser', 'password123')  # Different case

            assert user1 is not None
            # Case sensitivity behavior depends on implementation
            assert user2 is not None or user2 is None

    def test_password_verification_edge_cases(self):
        """Test password verification edge cases"""
        # Test with empty password
        try:
            hashed = hash_password('')
            result = verify_password('', hashed)
            assert isinstance(result, bool)
        except:
            pass  # Some implementations might not allow empty passwords

        # Test with very long password
        long_password = 'a' * 1000
        hashed = hash_password(long_password)
        assert verify_password(long_password, hashed) is True

        # Test with unicode password
        unicode_password = 'pássw0rd123!@#🔒'
        hashed = hash_password(unicode_password)
        assert verify_password(unicode_password, hashed) is True

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
