"""
Unit tests for authentication module
"""

import pytest
import json
from unittest.mock import Mock, patch
from auth import (
    hash_password, verify_password, validate_email, validate_password,
    UserService, create_user_tokens, revoke_token
)

class TestPasswordValidation:
    """Test password validation functions"""
    
    def test_hash_password(self):
        """Test password hashing"""
        password = "TestPassword123"
        hashed = hash_password(password)
        
        assert hashed != password
        assert len(hashed) > 0
        assert verify_password(password, hashed)
        assert not verify_password("wrongpassword", hashed)
    
    def test_validate_password_valid(self):
        """Test valid password validation"""
        valid_passwords = [
            "TestPass123",
            "MySecurePassword1",
            "ComplexP@ssw0rd"
        ]
        
        for password in valid_passwords:
            is_valid, message = validate_password(password)
            assert is_valid, f"Password '{password}' should be valid: {message}"
    
    def test_validate_password_invalid(self):
        """Test invalid password validation"""
        invalid_passwords = [
            ("short", "Password must be at least 8 characters long"),
            ("nouppercase123", "Password must contain at least one uppercase letter"),
            ("NOLOWERCASE123", "Password must contain at least one lowercase letter"),
            ("NoNumbers", "Password must contain at least one number"),
        ]
        
        for password, expected_message in invalid_passwords:
            is_valid, message = validate_password(password)
            assert not is_valid
            assert message == expected_message

class TestEmailValidation:
    """Test email validation"""
    
    def test_validate_email_valid(self):
        """Test valid email addresses"""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "123@numbers.com"
        ]
        
        for email in valid_emails:
            assert validate_email(email), f"Email '{email}' should be valid"
    
    def test_validate_email_invalid(self):
        """Test invalid email addresses"""
        invalid_emails = [
            "invalid-email",
            "@example.com",
            "user@",
            "user@.com",
            "user..name@example.com"
        ]
        
        for email in invalid_emails:
            assert not validate_email(email), f"Email '{email}' should be invalid"

class TestUserService:
    """Test UserService class"""
    
    @pytest.fixture
    def mock_db_connection(self):
        """Mock database connection"""
        mock_conn = Mock()
        mock_cur = Mock()
        mock_conn.cursor.return_value = mock_cur
        return mock_conn, mock_cur
    
    @pytest.fixture
    def user_service(self, mock_db_connection):
        """Create UserService with mock connection"""
        mock_conn, mock_cur = mock_db_connection
        
        def get_db_connection():
            return mock_conn
        
        return UserService(get_db_connection), mock_conn, mock_cur
    
    def test_create_user_success(self, user_service):
        """Test successful user creation"""
        service, mock_conn, mock_cur = user_service
        
        # Mock database response
        mock_cur.fetchone.return_value = (1,)  # user_id
        
        success, result = service.create_user(
            email="test@example.com",
            password="TestPass123",
            name="Test User"
        )
        
        assert success
        assert result == 1
        mock_cur.execute.assert_called()
        mock_conn.commit.assert_called()
    
    def test_create_user_invalid_email(self, user_service):
        """Test user creation with invalid email"""
        service, mock_conn, mock_cur = user_service
        
        success, message = service.create_user(
            email="invalid-email",
            password="TestPass123",
            name="Test User"
        )
        
        assert not success
        assert "Invalid email format" in message
        mock_cur.execute.assert_not_called()
    
    def test_create_user_invalid_password(self, user_service):
        """Test user creation with invalid password"""
        service, mock_conn, mock_cur = user_service
        
        success, message = service.create_user(
            email="test@example.com",
            password="weak",
            name="Test User"
        )
        
        assert not success
        assert "Password must be at least 8 characters long" in message
        mock_cur.execute.assert_not_called()
    
    def test_create_user_duplicate_email(self, user_service):
        """Test user creation with duplicate email"""
        service, mock_conn, mock_cur = user_service
        
        # Mock existing user
        mock_cur.fetchone.return_value = (1,)
        
        success, message = service.create_user(
            email="existing@example.com",
            password="TestPass123",
            name="Test User"
        )
        
        assert not success
        assert "User with this email already exists" in message
    
    def test_authenticate_user_success(self, user_service):
        """Test successful user authentication"""
        service, mock_conn, mock_cur = user_service
        
        # Mock user data
        hashed_password = hash_password("TestPass123")
        mock_cur.fetchone.return_value = (1, hashed_password, "Test User")
        
        success, result = service.authenticate_user(
            email="test@example.com",
            password="TestPass123"
        )
        
        assert success
        assert result["id"] == 1
        assert result["email"] == "test@example.com"
        assert result["name"] == "Test User"
    
    def test_authenticate_user_invalid_credentials(self, user_service):
        """Test authentication with invalid credentials"""
        service, mock_conn, mock_cur = user_service
        
        # Mock no user found
        mock_cur.fetchone.return_value = None
        
        success, message = service.authenticate_user(
            email="test@example.com",
            password="wrongpassword"
        )
        
        assert not success
        assert "Invalid email or password" in message
    
    def test_get_user_by_id_success(self, user_service):
        """Test getting user by ID"""
        service, mock_conn, mock_cur = user_service
        
        # Mock user data
        mock_cur.fetchone.return_value = (1, "test@example.com", "Test User", "2023-01-01")
        
        user = service.get_user_by_id(1)
        
        assert user is not None
        assert user["id"] == 1
        assert user["email"] == "test@example.com"
        assert user["name"] == "Test User"
    
    def test_get_user_by_id_not_found(self, user_service):
        """Test getting non-existent user"""
        service, mock_conn, mock_cur = user_service
        
        # Mock no user found
        mock_cur.fetchone.return_value = None
        
        user = service.get_user_by_id(999)
        
        assert user is None

class TestJWTTokens:
    """Test JWT token functions"""
    
    @patch('auth.create_access_token')
    @patch('auth.create_refresh_token')
    def test_create_user_tokens(self, mock_refresh_token, mock_access_token):
        """Test token creation"""
        mock_access_token.return_value = "access_token_123"
        mock_refresh_token.return_value = "refresh_token_456"
        
        access_token, refresh_token = create_user_tokens(1)
        
        assert access_token == "access_token_123"
        assert refresh_token == "refresh_token_456"
        mock_access_token.assert_called_with(identity=1)
        mock_refresh_token.assert_called_with(identity=1)
    
    @patch('auth.get_jwt')
    def test_revoke_token(self, mock_get_jwt):
        """Test token revocation"""
        mock_jwt = {"jti": "token_123"}
        mock_get_jwt.return_value = mock_jwt
        
        revoke_token()
        
        # Check if token was added to blocklist
        from auth import token_blocklist
        assert "token_123" in token_blocklist 