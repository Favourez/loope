#!/usr/bin/env python3
"""
Unit tests for database module
"""

import pytest
import sys
import os
import sqlite3
import tempfile
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import (
    init_database, get_db_connection, create_user, verify_user,
    create_emergency_report, get_emergency_reports, update_emergency_status,
    create_message, get_messages, get_first_aid_practices
)

class TestDatabaseConnection:
    """Test database connection functionality"""
    
    def test_get_db_connection_success(self):
        """Test successful database connection"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            # Initialize database
            with patch('database.DATABASE_PATH', db_path):
                init_database()
                conn = get_db_connection()
                assert conn is not None
                
                # Test that we can execute a query
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                assert len(tables) > 0
                conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_get_db_connection_failure(self):
        """Test database connection failure"""
        with patch('database.DATABASE_PATH', '/invalid/path/database.db'):
            conn = get_db_connection()
            assert conn is None

class TestDatabaseInitialization:
    """Test database initialization"""
    
    def test_init_database_creates_tables(self):
        """Test that init_database creates all required tables"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            with patch('database.DATABASE_PATH', db_path):
                init_database()
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check that all required tables exist
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = [row[0] for row in cursor.fetchall()]
                
                expected_tables = ['users', 'emergency_reports', 'messages', 'first_aid_practices']
                for table in expected_tables:
                    assert table in tables
                
                conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)
    
    def test_init_database_with_existing_database(self):
        """Test initializing database when it already exists"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        try:
            with patch('database.DATABASE_PATH', db_path):
                # Initialize twice
                init_database()
                init_database()  # Should not raise an error
                
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                tables = cursor.fetchall()
                assert len(tables) > 0
                conn.close()
        finally:
            if os.path.exists(db_path):
                os.unlink(db_path)

class TestUserOperations:
    """Test user-related database operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a test database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        with patch('database.DATABASE_PATH', db_path):
            init_database()
            yield db_path
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_create_user_success(self, test_db):
        """Test successful user creation"""
        with patch('database.DATABASE_PATH', test_db):
            result = create_user('testuser', 'password123', 'test@example.com', 'regular')
            assert result is True
    
    def test_create_user_duplicate(self, test_db):
        """Test creating duplicate user"""
        with patch('database.DATABASE_PATH', test_db):
            # Create user first time
            result1 = create_user('testuser', 'password123', 'test@example.com', 'regular')
            assert result1 is True
            
            # Try to create same user again
            result2 = create_user('testuser', 'password456', 'test2@example.com', 'regular')
            assert result2 is False
    
    def test_verify_user_valid(self, test_db):
        """Test verifying valid user credentials"""
        with patch('database.DATABASE_PATH', test_db):
            # Create user first
            create_user('testuser', 'password123', 'test@example.com', 'regular')
            
            # Verify credentials
            user = verify_user('testuser', 'password123')
            assert user is not None
            assert user['username'] == 'testuser'
            assert user['email'] == 'test@example.com'
    
    def test_verify_user_invalid_username(self, test_db):
        """Test verifying with invalid username"""
        with patch('database.DATABASE_PATH', test_db):
            user = verify_user('nonexistent', 'password123')
            assert user is None
    
    def test_verify_user_invalid_password(self, test_db):
        """Test verifying with invalid password"""
        with patch('database.DATABASE_PATH', test_db):
            # Create user first
            create_user('testuser', 'password123', 'test@example.com', 'regular')
            
            # Try with wrong password
            user = verify_user('testuser', 'wrongpassword')
            assert user is None

class TestEmergencyOperations:
    """Test emergency report database operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a test database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        with patch('database.DATABASE_PATH', db_path):
            init_database()
            yield db_path
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_create_emergency_report_success(self, test_db):
        """Test successful emergency report creation"""
        with patch('database.DATABASE_PATH', test_db):
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
            
            emergency_id = create_emergency_report(emergency_data)
            assert emergency_id is not None
            assert isinstance(emergency_id, int)
    
    def test_create_emergency_report_missing_data(self, test_db):
        """Test emergency report creation with missing data"""
        with patch('database.DATABASE_PATH', test_db):
            emergency_data = {
                'emergency_type': 'fire'
                # Missing required fields
            }
            
            emergency_id = create_emergency_report(emergency_data)
            assert emergency_id is None
    
    def test_get_emergency_reports(self, test_db):
        """Test retrieving emergency reports"""
        with patch('database.DATABASE_PATH', test_db):
            # Create test emergency
            emergency_data = {
                'emergency_type': 'medical',
                'location': 'Test Hospital',
                'description': 'Test medical emergency',
                'severity': 'medium',
                'latitude': 3.8634,
                'longitude': 11.5167,
                'reporter_name': 'Test User',
                'reporter_phone': '+237123456789'
            }
            
            emergency_id = create_emergency_report(emergency_data)
            assert emergency_id is not None
            
            # Retrieve reports
            reports = get_emergency_reports()
            assert len(reports) > 0
            assert any(report['id'] == emergency_id for report in reports)
    
    def test_update_emergency_status_success(self, test_db):
        """Test successful emergency status update"""
        with patch('database.DATABASE_PATH', test_db):
            # Create test emergency
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
            
            emergency_id = create_emergency_report(emergency_data)
            assert emergency_id is not None
            
            # Update status
            result = update_emergency_status(emergency_id, 'responding')
            assert result is True
    
    def test_update_emergency_status_invalid_id(self, test_db):
        """Test updating status for non-existent emergency"""
        with patch('database.DATABASE_PATH', test_db):
            result = update_emergency_status(999, 'responding')
            assert result is False

class TestMessageOperations:
    """Test message-related database operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a test database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        with patch('database.DATABASE_PATH', db_path):
            init_database()
            yield db_path
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_create_message_success(self, test_db):
        """Test successful message creation"""
        with patch('database.DATABASE_PATH', test_db):
            message_data = {
                'content': 'Test community message',
                'message_type': 'info',
                'sender': 'Test User'
            }
            
            message_id = create_message(message_data)
            assert message_id is not None
            assert isinstance(message_id, int)
    
    def test_get_messages(self, test_db):
        """Test retrieving messages"""
        with patch('database.DATABASE_PATH', test_db):
            # Create test message
            message_data = {
                'content': 'Test community message',
                'message_type': 'info',
                'sender': 'Test User'
            }
            
            message_id = create_message(message_data)
            assert message_id is not None
            
            # Retrieve messages
            messages = get_messages()
            assert len(messages) > 0
            assert any(msg['id'] == message_id for msg in messages)

class TestFirstAidOperations:
    """Test first aid practices database operations"""
    
    @pytest.fixture
    def test_db(self):
        """Create a test database"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            db_path = tmp_file.name
        
        with patch('database.DATABASE_PATH', db_path):
            init_database()
            yield db_path
        
        if os.path.exists(db_path):
            os.unlink(db_path)
    
    def test_get_first_aid_practices(self, test_db):
        """Test retrieving first aid practices"""
        with patch('database.DATABASE_PATH', test_db):
            practices = get_first_aid_practices()
            assert isinstance(practices, list)
            assert len(practices) > 0
            
            # Check structure of first practice
            if practices:
                practice = practices[0]
                assert 'id' in practice
                assert 'title' in practice
                assert 'description' in practice

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
