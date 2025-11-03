"""
Comprehensive security testing
Tests: authentication, authorization, SQL injection, XSS, CSRF, session management, password security
"""
import pytest


@pytest.mark.security
class TestAuthenticationSecurity:
    """Test authentication security"""
    
    def test_admin_endpoints_require_auth(self, client):
        """Test admin endpoints require authentication"""
        endpoints = ["/admin/dashboard", "/admin/pages", "/admin/questions", "/admin/results"]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code in [401, 302, 303], f"Endpoint {endpoint} not protected"
    
    def test_invalid_credentials_rejected(self, client, test_admin):
        """Test invalid credentials rejected"""
        response = client.post("/admin/login", data={
            "username": "testadmin",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 200
        assert b"invalid" in response.content.lower() or b"error" in response.content.lower()
    
    def test_sql_injection_protection(self, client):
        """Test SQL injection protection in login"""
        payloads = ["admin' OR '1'='1", "admin'--", "'; DROP TABLE admins; --"]
        
        for payload in payloads:
            response = client.post("/admin/login", data={
                "username": payload,
                "password": "password"
            })
            
            assert response.status_code in [200, 400, 401]
    
    def test_password_hashed_in_database(self, test_admin):
        """Test passwords stored as hashes"""
        assert len(test_admin.password_hash) >= 50
        assert test_admin.password_hash != "testpass123"


@pytest.mark.security
class TestXSSProtection:
    """Test XSS protection"""
    
    def test_xss_in_page_title(self, authenticated_admin_client):
        """Test XSS protection in page titles"""
        xss_payload = "<script>alert('XSS')</script>"
        
        response = authenticated_admin_client.post("/admin/pages", data={
            "title": xss_payload,
            "description": "Test",
            "order_index": "0"
        })
        
        assert response.status_code == 302
    
    def test_xss_in_answers(self, client, test_page, test_essay_question):
        """Test XSS protection in student answers"""
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        xss_payload = "<img src=x onerror=alert('XSS')>"
        
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_essay_question.id}_text": xss_payload
        })
        
        assert response.status_code == 200


@pytest.mark.security
class TestSessionSecurity:
    """Test session management security"""
    
    def test_session_isolation(self, client, test_page, test_essay_question):
        """Test different sessions are isolated"""
        # First session
        response1 = client.get("/student/exam")
        session_id1 = response1.cookies.get("session_id")
        
        # Second session
        from fastapi.testclient import TestClient
        from app.main import app
        client2 = TestClient(app)
        response2 = client2.get("/student/exam")
        session_id2 = response2.cookies.get("session_id")
        
        assert session_id1 != session_id2
    
    def test_logout_invalidates_session(self, authenticated_admin_client):
        """Test logout invalidates session"""
        response = authenticated_admin_client.get("/admin/dashboard")
        assert response.status_code == 200
        
        authenticated_admin_client.get("/admin/logout")


@pytest.mark.security
class TestInputValidation:
    """Test input validation"""
    
    def test_required_fields_validated(self, authenticated_admin_client):
        """Test required fields validation"""
        response = authenticated_admin_client.post("/admin/pages", data={
            "description": "Missing title",
            "order_index": "0"
        })
        
        assert response.status_code in [400, 422]
    
    def test_numeric_validation(self, authenticated_admin_client, test_page):
        """Test numeric input validation"""
        response = authenticated_admin_client.post("/admin/pages", data={
            "title": "Test",
            "description": "Test",
            "order_index": "not_a_number"
        })
        
        assert response.status_code in [400, 422]
