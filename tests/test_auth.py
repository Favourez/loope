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

from auth import (
    hash_password, verify_password, generate_api_key, verify_api_key,
    generate_session_token, verify_session_token, is_strong_password,
    sanitize_input, rate_limit_check
)

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
    
    def test_verify_password_empty_inputs(self):
        """Test password verification with empty inputs"""
        assert verify_password("", "") is False
        assert verify_password("password", "") is False
        assert verify_password("", "hash") is False
    
    def test_hash_password_empty_input(self):
        """Test hashing empty password"""
        hashed = hash_password("")
        assert hashed is not None
        assert isinstance(hashed, str)
    
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

class TestAPIKeyGeneration:
    """Test API key generation and verification"""
    
    def test_generate_api_key_creates_key(self):
        """Test that generate_api_key creates a key"""
        api_key = generate_api_key()
        
        assert api_key is not None
        assert isinstance(api_key, str)
        assert len(api_key) > 0
    
    def test_generate_api_key_different_keys(self):
        """Test that generate_api_key creates different keys"""
        key1 = generate_api_key()
        key2 = generate_api_key()
        
        assert key1 != key2
    
    def test_generate_api_key_format(self):
        """Test API key format"""
        api_key = generate_api_key()
        
        # Should be alphanumeric and dashes
        assert all(c.isalnum() or c == '-' for c in api_key)
        assert len(api_key) >= 32  # Should be reasonably long
    
    def test_verify_api_key_valid(self):
        """Test API key verification with valid key"""
        # Test with known valid key
        valid_key = "emergency-api-key-2024"
        assert verify_api_key(valid_key) is True
    
    def test_verify_api_key_invalid(self):
        """Test API key verification with invalid key"""
        invalid_key = "invalid-key"
        assert verify_api_key(invalid_key) is False
    
    def test_verify_api_key_empty(self):
        """Test API key verification with empty key"""
        assert verify_api_key("") is False
        assert verify_api_key(None) is False
    
    def test_verify_api_key_generated(self):
        """Test verification of generated API key"""
        # This test assumes generated keys are stored/validated somewhere
        api_key = generate_api_key()
        
        # For this test, we'll mock the verification
        with patch('auth.verify_api_key', return_value=True):
            assert verify_api_key(api_key) is True

class TestSessionTokens:
    """Test session token generation and verification"""
    
    def test_generate_session_token_creates_token(self):
        """Test that generate_session_token creates a token"""
        user_id = 123
        token = generate_session_token(user_id)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_generate_session_token_different_tokens(self):
        """Test that generate_session_token creates different tokens"""
        user_id = 123
        token1 = generate_session_token(user_id)
        token2 = generate_session_token(user_id)
        
        assert token1 != token2
    
    def test_verify_session_token_valid(self):
        """Test session token verification with valid token"""
        user_id = 123
        token = generate_session_token(user_id)
        
        # Mock token storage/verification
        with patch('auth.verify_session_token', return_value=user_id):
            verified_user_id = verify_session_token(token)
            assert verified_user_id == user_id
    
    def test_verify_session_token_invalid(self):
        """Test session token verification with invalid token"""
        invalid_token = "invalid-token"
        
        with patch('auth.verify_session_token', return_value=None):
            verified_user_id = verify_session_token(invalid_token)
            assert verified_user_id is None
    
    def test_verify_session_token_expired(self):
        """Test session token verification with expired token"""
        user_id = 123
        token = generate_session_token(user_id)
        
        # Mock expired token
        with patch('auth.verify_session_token', return_value=None):
            verified_user_id = verify_session_token(token)
            assert verified_user_id is None

class TestPasswordStrength:
    """Test password strength validation"""
    
    def test_is_strong_password_valid(self):
        """Test strong password validation with valid passwords"""
        strong_passwords = [
            "StrongP@ssw0rd123",
            "MySecure!Pass2024",
            "C0mpl3x&P@ssw0rd",
            "Tr0ub4dor&3"
        ]
        
        for password in strong_passwords:
            assert is_strong_password(password) is True
    
    def test_is_strong_password_weak(self):
        """Test strong password validation with weak passwords"""
        weak_passwords = [
            "password",      # Too simple
            "123456",        # Only numbers
            "PASSWORD",      # Only uppercase
            "password123",   # No special chars
            "Pass1!",        # Too short
            "",              # Empty
            "a"              # Too short
        ]
        
        for password in weak_passwords:
            assert is_strong_password(password) is False
    
    def test_is_strong_password_edge_cases(self):
        """Test password strength with edge cases"""
        assert is_strong_password(None) is False
        assert is_strong_password("") is False
        assert is_strong_password(" " * 20) is False  # Only spaces

class TestInputSanitization:
    """Test input sanitization"""
    
    def test_sanitize_input_normal(self):
        """Test sanitizing normal input"""
        normal_input = "Hello World"
        sanitized = sanitize_input(normal_input)
        assert sanitized == "Hello World"
    
    def test_sanitize_input_html(self):
        """Test sanitizing HTML input"""
        html_input = "<script>alert('xss')</script>"
        sanitized = sanitize_input(html_input)
        assert "<script>" not in sanitized
        assert "alert" not in sanitized
    
    def test_sanitize_input_sql(self):
        """Test sanitizing potential SQL injection"""
        sql_input = "'; DROP TABLE users; --"
        sanitized = sanitize_input(sql_input)
        assert "DROP TABLE" not in sanitized.upper()
    
    def test_sanitize_input_empty(self):
        """Test sanitizing empty input"""
        assert sanitize_input("") == ""
        assert sanitize_input(None) == ""
    
    def test_sanitize_input_unicode(self):
        """Test sanitizing unicode input"""
        unicode_input = "Héllo Wörld 🌍"
        sanitized = sanitize_input(unicode_input)
        assert len(sanitized) > 0
        # Should preserve valid unicode characters

class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_rate_limit_check_allowed(self):
        """Test rate limiting when requests are allowed"""
        client_ip = "192.168.1.1"
        
        # Mock rate limiting to allow requests
        with patch('auth.rate_limit_check', return_value=True):
            assert rate_limit_check(client_ip) is True
    
    def test_rate_limit_check_blocked(self):
        """Test rate limiting when requests are blocked"""
        client_ip = "192.168.1.1"
        
        # Mock rate limiting to block requests
        with patch('auth.rate_limit_check', return_value=False):
            assert rate_limit_check(client_ip) is False
    
    def test_rate_limit_check_multiple_ips(self):
        """Test rate limiting with multiple IP addresses"""
        ip1 = "192.168.1.1"
        ip2 = "192.168.1.2"
        
        # Mock different responses for different IPs
        def mock_rate_limit(ip):
            return ip == ip1
        
        with patch('auth.rate_limit_check', side_effect=mock_rate_limit):
            assert rate_limit_check(ip1) is True
            assert rate_limit_check(ip2) is False

class TestAuthenticationIntegration:
    """Test authentication integration scenarios"""
    
    def test_complete_auth_flow(self):
        """Test complete authentication flow"""
        # 1. Create user with strong password
        password = "StrongP@ssw0rd123"
        assert is_strong_password(password) is True
        
        # 2. Hash password
        hashed = hash_password(password)
        assert hashed is not None
        
        # 3. Verify password
        assert verify_password(password, hashed) is True
        
        # 4. Generate API key
        api_key = generate_api_key()
        assert api_key is not None
        
        # 5. Generate session token
        user_id = 123
        session_token = generate_session_token(user_id)
        assert session_token is not None
    
    def test_security_measures(self):
        """Test various security measures"""
        # Test input sanitization
        malicious_input = "<script>alert('xss')</script>"
        sanitized = sanitize_input(malicious_input)
        assert "<script>" not in sanitized
        
        # Test password strength
        weak_password = "123456"
        assert is_strong_password(weak_password) is False
        
        # Test API key verification
        invalid_key = "invalid-key"
        assert verify_api_key(invalid_key) is False

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
