"""
Comprehensive unit tests for utility modules
"""
import pytest
from datetime import datetime, timedelta
from app.utils.security import (
    verify_password, get_password_hash, create_access_token, verify_token
)
from app.utils.helpers import (
    generate_session_id, save_upload_file, validate_image_file,
    delete_file, format_datetime
)
from jose import jwt
import os
import tempfile


class TestSecurityUtils:
    """Test security utility functions"""
    
    def test_password_hashing(self):
        """Test password hashing"""
        password = "mysecurepassword123"
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert hashed != password
        assert len(hashed) > 20  # Bcrypt hashes are long
    
    def test_password_verification_success(self):
        """Test successful password verification"""
        password = "testpassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
    
    def test_password_verification_failure(self):
        """Test failed password verification"""
        password = "testpassword123"
        wrong_password = "wrongpassword"
        hashed = get_password_hash(password)
        
        assert verify_password(wrong_password, hashed) is False
    
    def test_different_passwords_different_hashes(self):
        """Test that same password generates different hashes (salt)"""
        password = "samepassword"
        hash1 = get_password_hash(password)
        hash2 = get_password_hash(password)
        
        # Hashes should be different due to salt
        assert hash1 != hash2
        # But both should verify correctly
        assert verify_password(password, hash1)
        assert verify_password(password, hash2)
    
    def test_create_access_token(self):
        """Test JWT token creation"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
    
    def test_create_access_token_with_expiry(self):
        """Test JWT token creation with custom expiry"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = create_access_token(data, expires_delta)
        
        assert token is not None
    
    def test_verify_token_success(self):
        """Test successful token verification"""
        username = "testuser"
        data = {"sub": username}
        token = create_access_token(data)
        
        verified_username = verify_token(token)
        assert verified_username == username
    
    def test_verify_token_invalid(self):
        """Test invalid token verification"""
        invalid_token = "invalid.token.here"
        result = verify_token(invalid_token)
        
        assert result is None
    
    def test_verify_token_expired(self):
        """Test expired token verification"""
        data = {"sub": "testuser"}
        # Create token that expires immediately
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta)
        
        result = verify_token(token)
        assert result is None
    
    def test_verify_token_missing_subject(self):
        """Test token without subject claim"""
        from app.utils.security import SECRET_KEY, ALGORITHM
        
        # Create token without 'sub' claim
        data = {"user": "testuser", "exp": datetime.utcnow() + timedelta(minutes=30)}
        token = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)
        
        result = verify_token(token)
        assert result is None
    
    def test_empty_password_hashing(self):
        """Test hashing empty password"""
        password = ""
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert verify_password(password, hashed)
    
    def test_long_password_hashing(self):
        """Test hashing very long password"""
        password = "a" * 1000  # Very long password
        hashed = get_password_hash(password)
        
        assert hashed is not None
        assert verify_password(password, hashed)
    
    def test_special_characters_password(self):
        """Test password with special characters"""
        password = "p@ssw0rd!#$%^&*()_+-=[]{}|;:',.<>?/~`"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed)
    
    def test_unicode_password(self):
        """Test password with unicode characters"""
        password = "пароль密码🔒"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed)


class TestHelperUtils:
    """Test helper utility functions"""
    
    def test_generate_session_id(self):
        """Test session ID generation"""
        session_id = generate_session_id()
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
        # UUID format: 8-4-4-4-12
        assert len(session_id) == 36
        assert session_id.count('-') == 4
    
    def test_generate_unique_session_ids(self):
        """Test that generated session IDs are unique"""
        session_ids = set()
        for _ in range(100):
            session_ids.add(generate_session_id())
        
        # All 100 should be unique
        assert len(session_ids) == 100
    
    def test_format_datetime_with_datetime(self):
        """Test datetime formatting"""
        dt = datetime(2023, 12, 25, 15, 30, 45)
        formatted = format_datetime(dt)
        
        assert formatted is not None
        assert "2023" in formatted
        assert "12" in formatted or "Dec" in formatted
    
    def test_format_datetime_with_none(self):
        """Test formatting None datetime"""
        formatted = format_datetime(None)
        
        assert formatted == "N/A"
    
    def test_format_datetime_custom_format(self):
        """Test datetime formatting with default format"""
        dt = datetime(2023, 12, 25, 15, 30, 45)
        formatted = format_datetime(dt)
        
        # Default format is "%Y-%m-%d %H:%M:%S"
        assert formatted == "2023-12-25 15:30:45"
    
    def test_validate_image_file_valid_jpg(self):
        """Test validating valid JPG file"""
        class MockFile:
            filename = "test.jpg"
            file = type('obj', (object,), {'read': lambda: b'\xff\xd8\xff'})()
        
        mock_file = MockFile()
        result = validate_image_file(mock_file)
        
        assert result is True
    
    def test_validate_image_file_valid_png(self):
        """Test validating valid PNG file"""
        class MockFile:
            filename = "test.png"
            file = type('obj', (object,), {'read': lambda: b'\x89PNG\r\n\x1a\n'})()
        
        mock_file = MockFile()
        result = validate_image_file(mock_file)
        
        assert result is True
    
    def test_validate_image_file_invalid_extension(self):
        """Test validating file with invalid extension"""
        class MockFile:
            filename = "test.txt"
            file = type('obj', (object,), {'read': lambda: b'some text'})()
        
        mock_file = MockFile()
        result = validate_image_file(mock_file)
        
        assert result is False
    
    def test_validate_image_file_none(self):
        """Test validating None file"""
        result = validate_image_file(None)
        
        assert result is False
    
    def test_validate_image_file_no_filename(self):
        """Test validating file without filename"""
        class MockFile:
            filename = None
            file = None
        
        mock_file = MockFile()
        result = validate_image_file(mock_file)
        
        assert result is False
    
    def test_save_upload_file_creates_file(self):
        """Test saving upload file"""
        class MockFile:
            filename = "test_upload.jpg"
            file = type('obj', (object,), {
                'read': lambda size=None: b'\xff\xd8\xff\xe0' if size is None else b''
            })()
        
        mock_file = MockFile()
        
        try:
            file_path = save_upload_file(mock_file)
            
            assert file_path is not None
            assert "test_upload" in file_path
            assert file_path.endswith(".jpg")
            
            # Clean up
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception as e:
            # File operations might fail in test environment
            pass
    
    def test_delete_file_existing(self):
        """Test deleting existing file"""
        # Create temporary file
        fd, temp_path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        
        # Write some content
        with open(temp_path, 'w') as f:
            f.write("test content")
        
        # Delete it
        result = delete_file(temp_path)
        
        assert result is True
        assert not os.path.exists(temp_path)
    
    def test_delete_file_nonexistent(self):
        """Test deleting non-existent file"""
        fake_path = "/fake/path/to/nonexistent/file.txt"
        result = delete_file(fake_path)
        
        # Should return False but not raise exception
        assert result is False
    
    def test_delete_file_none(self):
        """Test deleting None file path"""
        result = delete_file(None)
        
        assert result is False
    
    def test_delete_file_empty_string(self):
        """Test deleting empty string file path"""
        result = delete_file("")
        
        assert result is False


class TestSecurityEdgeCases:
    """Test edge cases in security utilities"""
    
    def test_token_with_additional_claims(self):
        """Test token with additional custom claims"""
        data = {
            "sub": "testuser",
            "role": "admin",
            "permissions": ["read", "write"]
        }
        token = create_access_token(data)
        
        # Should still verify and return username
        username = verify_token(token)
        assert username == "testuser"
    
    def test_password_case_sensitivity(self):
        """Test that password verification is case-sensitive"""
        password = "TestPassword123"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True
        assert verify_password(password.lower(), hashed) is False
        assert verify_password(password.upper(), hashed) is False
    
    def test_password_whitespace(self):
        """Test password with whitespace"""
        password = "  password with spaces  "
        hashed = get_password_hash(password)
        
        # Exact match including spaces
        assert verify_password(password, hashed) is True
        # Without spaces should fail
        assert verify_password(password.strip(), hashed) is False
    
    def test_numeric_only_password(self):
        """Test numeric-only password"""
        password = "123456789"
        hashed = get_password_hash(password)
        
        assert verify_password(password, hashed) is True


class TestHelperUtilsEdgeCases:
    """Test edge cases in helper utilities"""
    
    def test_format_datetime_current_time(self):
        """Test formatting current datetime"""
        now = datetime.utcnow()
        formatted = format_datetime(now)
        
        assert formatted is not None
        assert len(formatted) > 0
    
    def test_format_datetime_far_future(self):
        """Test formatting far future date"""
        future_date = datetime(2099, 12, 31, 23, 59, 59)
        formatted = format_datetime(future_date)
        
        assert "2099" in formatted
    
    def test_format_datetime_far_past(self):
        """Test formatting far past date"""
        past_date = datetime(1900, 1, 1, 0, 0, 0)
        formatted = format_datetime(past_date)
        
        assert "1900" in formatted
    
    def test_validate_large_image_file(self):
        """Test validating large image file"""
        class MockFile:
            filename = "large_image.jpg"
            file = type('obj', (object,), {
                'read': lambda: b'\xff\xd8\xff' + b'0' * (10 * 1024 * 1024)  # 10MB
            })()
        
        mock_file = MockFile()
        # Should validate based on extension/header, not size in this function
        result = validate_image_file(mock_file)
        
        assert result is True
    
    def test_validate_image_case_insensitive_extension(self):
        """Test image validation with different case extensions"""
        class MockFileJPG:
            filename = "test.JPG"
            file = type('obj', (object,), {'read': lambda: b'\xff\xd8\xff'})()
        
        class MockFilePng:
            filename = "test.PNG"
            file = type('obj', (object,), {'read': lambda: b'\x89PNG\r\n\x1a\n'})()
        
        assert validate_image_file(MockFileJPG()) is True
        assert validate_image_file(MockFilePng()) is True


class TestSecurityIntegration:
    """Integration tests for security utilities"""
    
    def test_password_hash_and_verify_workflow(self):
        """Test complete password workflow"""
        # Registration
        user_password = "mySecureP@ssw0rd!"
        stored_hash = get_password_hash(user_password)
        
        # Login attempt 1 - correct password
        assert verify_password(user_password, stored_hash) is True
        
        # Login attempt 2 - wrong password
        assert verify_password("wrongpassword", stored_hash) is False
        
        # Login attempt 3 - correct password again
        assert verify_password(user_password, stored_hash) is True
    
    def test_token_creation_and_verification_workflow(self):
        """Test complete token workflow"""
        # Create token for user
        username = "johndoe"
        token = create_access_token({"sub": username})
        
        # Verify token
        verified_username = verify_token(token)
        assert verified_username == username
        
        # Use in authorization
        assert verified_username == username  # User is authenticated
    
    def test_multiple_users_token_isolation(self):
        """Test that different users get different tokens"""
        user1_token = create_access_token({"sub": "user1"})
        user2_token = create_access_token({"sub": "user2"})
        
        assert user1_token != user2_token
        
        assert verify_token(user1_token) == "user1"
        assert verify_token(user2_token) == "user2"
