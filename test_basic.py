"""
Simple test to verify pytest is working correctly
"""

def test_basic_functionality():
    """Test basic Python functionality"""
    assert 1 + 1 == 2
    assert "hello".upper() == "HELLO"
    assert [1, 2, 3] == [1, 2, 3]


def test_application_imports():
    """Test that we can import our application modules"""
    try:
        from app.main import app
        assert app is not None
    except ImportError as e:
        assert False, f"Failed to import app: {e}"


def test_database_models():
    """Test that database models can be imported"""
    try:
        from app.models.database import Base
        from app.models import Admin, Page, Question
        assert Base is not None
        assert Admin is not None
        assert Page is not None
        assert Question is not None
    except ImportError as e:
        assert False, f"Failed to import models: {e}"


def test_utilities():
    """Test utility functions"""
    try:
        from app.utils.security import get_password_hash, verify_password
        
        # Test password hashing
        password = "test123"
        hashed = get_password_hash(password)
        assert hashed != password
        assert verify_password(password, hashed) is True
        assert verify_password("wrong", hashed) is False
        
    except ImportError as e:
        assert False, f"Failed to import utilities: {e}"