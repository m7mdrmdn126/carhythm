import pytest
from unittest.mock import Mock, patch
from app.utils.security import verify_password, get_password_hash, create_access_token, verify_token
from app.utils.helpers import generate_session_id, validate_image_file, format_datetime
from datetime import datetime, timedelta


class TestSecurity:
    """Test security utility functions"""
    
    def test_password_hashing(self):
        """Test password hashing and verification"""
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        # Hash should not be the same as original password
        assert hashed != password
        
        # Verification should work with correct password
        assert verify_password(password, hashed) is True
        
        # Verification should fail with wrong password
        assert verify_password("wrong_password", hashed) is False
    
    def test_access_token_creation_and_verification(self):
        """Test JWT token creation and verification"""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        
        # Token should be a string
        assert isinstance(token, str)
        
        # Should be able to verify and extract username
        username = verify_token(token)
        assert username == "testuser"
    
    def test_token_expiration(self):
        """Test token expiration"""
        data = {"sub": "testuser"}
        expires_delta = timedelta(seconds=-1)  # Expired token
        expired_token = create_access_token(data, expires_delta)
        
        # Expired token should return None
        username = verify_token(expired_token)
        assert username is None
    
    def test_invalid_token(self):
        """Test invalid token handling"""
        invalid_token = "invalid.token.here"
        username = verify_token(invalid_token)
        assert username is None


class TestHelpers:
    """Test helper utility functions"""
    
    def test_generate_session_id(self):
        """Test session ID generation"""
        session_id1 = generate_session_id()
        session_id2 = generate_session_id()
        
        # Should be strings
        assert isinstance(session_id1, str)
        assert isinstance(session_id2, str)
        
        # Should be unique
        assert session_id1 != session_id2
        
        # Should be valid UUID format (36 characters with hyphens)
        assert len(session_id1) == 36
        assert session_id1.count('-') == 4
    
    def test_validate_image_file(self):
        """Test image file validation"""
        # Mock valid image file
        mock_valid_file = Mock()
        mock_valid_file.filename = "test.jpg"
        assert validate_image_file(mock_valid_file) is True
        
        mock_valid_file.filename = "test.png"
        assert validate_image_file(mock_valid_file) is True
        
        mock_valid_file.filename = "test.gif"
        assert validate_image_file(mock_valid_file) is True
        
        # Mock invalid file
        mock_invalid_file = Mock()
        mock_invalid_file.filename = "test.txt"
        assert validate_image_file(mock_invalid_file) is False
        
        mock_invalid_file.filename = "test.pdf"
        assert validate_image_file(mock_invalid_file) is False
        
        # No filename
        mock_no_name = Mock()
        mock_no_name.filename = None
        assert validate_image_file(mock_no_name) is False
    
    def test_format_datetime(self):
        """Test datetime formatting"""
        test_datetime = datetime(2025, 1, 15, 14, 30, 45)
        formatted = format_datetime(test_datetime)
        assert formatted == "2025-01-15 14:30:45"
        
        # Test with None
        formatted_none = format_datetime(None)
        assert formatted_none == "N/A"
    
    @patch('os.makedirs')
    @patch('builtins.open')
    def test_save_upload_file(self, mock_open, mock_makedirs):
        """Test file upload saving"""
        from app.utils.helpers import save_upload_file
        
        # Mock file
        mock_file = Mock()
        mock_file.filename = "test.jpg"
        mock_file.file.read.return_value = b"fake image data"
        
        # Mock file operations
        mock_open.return_value.__enter__.return_value = Mock()
        
        # Test save
        result = save_upload_file(mock_file)
        
        # Should return a path
        assert result is not None
        assert result.startswith("static/uploads/images/")
        assert result.endswith(".jpg")
        
        # Should create directory
        mock_makedirs.assert_called_once()
    
    def test_save_upload_file_no_file(self):
        """Test save_upload_file with no file"""
        from app.utils.helpers import save_upload_file
        
        result = save_upload_file(None)
        assert result is None