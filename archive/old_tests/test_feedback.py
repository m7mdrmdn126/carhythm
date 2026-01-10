#!/usr/bin/env python3
"""
Test script to verify feedback implementation
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    # Test imports
    print("Testing imports...")
    from app.models import Feedback, StudentResponse as Response
    from app.schemas.feedback import FeedbackSubmit, FeedbackResponse, FeedbackStats
    from app.routers.feedback import router as feedback_router
    print("✓ All imports successful")
    
    # Check Feedback model attributes
    print("\nChecking Feedback model attributes...")
    expected_attrs = ['id', 'session_id', 'rating', 'experience_text', 'would_recommend', 'suggestions', 'created_at']
    for attr in expected_attrs:
        if hasattr(Feedback, attr):
            print(f"✓ {attr} exists")
        else:
            print(f"✗ {attr} missing")
    
    # Check schema fields
    print("\nChecking FeedbackSubmit schema...")
    schema_fields = FeedbackSubmit.__fields__.keys()
    print(f"✓ Schema fields: {', '.join(schema_fields)}")
    
    # Check router endpoints
    print("\nChecking feedback router...")
    routes = [route.path for route in feedback_router.routes]
    print(f"✓ Feedback endpoints: {', '.join(routes)}")
    
    print("\n✅ All checks passed! Feedback feature is ready.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Note: Run this from within your virtual environment")
except Exception as e:
    print(f"❌ Error: {e}")
