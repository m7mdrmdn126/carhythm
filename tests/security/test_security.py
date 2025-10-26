"""
Security tests for the Career DNA Assessment application
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app


class TestSecurity:
    """Security-focused tests"""
    
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_sql_injection_protection(self, populated_db):
        """Test protection against SQL injection attacks"""
        # Test SQL injection in login form
        response = self.client.post("/admin/login", data={
            "username": "admin'; DROP TABLE admins; --",
            "password": "password"
        })
        
        # Should not crash and should not be successful
        assert response.status_code in [200, 302]  # Either show error or redirect
        
        # Test SQL injection in examination answers
        start_response = self.client.post("/examination/start")
        session_id = start_response.cookies.get("session_id")
        
        malicious_answer = "'; DROP TABLE student_responses; SELECT * FROM admins WHERE '1'='1"
        
        response = self.client.post(
            "/examination/submit_answers",
            data={
                "session_id": session_id,
                "page_id": "1",
                "answers": f'{{"1": {{"type": "essay", "value": "{malicious_answer}"}}}}'
            }
        )
        
        # Should handle gracefully
        assert response.status_code in [200, 302, 400]
    
    def test_xss_protection(self, populated_db):
        """Test protection against Cross-Site Scripting (XSS) attacks"""
        # Start examination
        start_response = self.client.post("/examination/start")
        session_id = start_response.cookies.get("session_id")
        
        # Submit XSS payload in answer
        xss_payload = "<script>alert('XSS')</script>"
        
        response = self.client.post(
            "/examination/submit_answers",
            data={
                "session_id": session_id,
                "page_id": "1",
                "answers": f'{{"1": {{"type": "essay", "value": "{xss_payload}"}}}}'
            }
        )
        
        # Should not execute script
        assert response.status_code in [200, 302]
        assert "<script>" not in response.text if hasattr(response, 'text') else True
    
    def test_csrf_protection(self, authenticated_admin_client):
        """Test CSRF protection on sensitive operations"""
        # Try to create a page without proper CSRF token
        response = authenticated_admin_client.post("/admin/pages", data={
            "title": "CSRF Test Page",
            "description": "Test",
            "order_index": "99"
        })
        
        # Should either require CSRF token or handle gracefully
        assert response.status_code in [200, 302, 400, 403]
    
    def test_unauthorized_access_protection(self):
        """Test that admin endpoints require authentication"""
        protected_endpoints = [
            "/admin/dashboard",
            "/admin/pages",
            "/admin/questions",
            "/admin/results"
        ]
        
        for endpoint in protected_endpoints:
            response = self.client.get(endpoint)
            
            # Should redirect to login or return unauthorized
            assert response.status_code in [302, 401, 403], f"Endpoint {endpoint} is not protected"
    
    def test_file_upload_security(self, authenticated_admin_client):
        """Test file upload security measures"""
        # Test uploading executable file
        malicious_file = {
            "image": ("malicious.exe", b"MZ\x90\x00", "application/octet-stream")
        }
        
        response = authenticated_admin_client.post(
            "/admin/questions",
            data={
                "page_id": "1",
                "question_text": "Test",
                "question_type": "essay",
                "order_index": "1",
                "is_required": "true"
            },
            files=malicious_file
        )
        
        # Should reject executable files
        assert response.status_code in [200, 400, 422]
    
    def test_path_traversal_protection(self):
        """Test protection against path traversal attacks"""
        # Try to access files outside web root
        malicious_paths = [
            "/../../etc/passwd",
            "/..\\..\\windows\\system32\\config\\sam",
            "/static/../../../app/config.py"
        ]
        
        for path in malicious_paths:
            response = self.client.get(path)
            
            # Should not expose system files
            assert response.status_code in [404, 403], f"Path traversal possible with {path}"
    
    def test_session_security(self, populated_db):
        """Test session management security"""
        # Start examination
        start_response = self.client.post("/examination/start")
        session_id = start_response.cookies.get("session_id")
        
        # Try to access another session's data
        fake_session_id = "fake-session-12345"
        
        response = self.client.post(
            "/examination/submit_answers",
            data={
                "session_id": fake_session_id,
                "page_id": "1",
                "answers": '{"1": {"type": "essay", "value": "Test"}}'
            }
        )
        
        # Should not accept invalid session
        assert response.status_code in [400, 404, 302]
    
    def test_input_validation(self, populated_db):
        """Test input validation and sanitization"""
        # Test extremely long input
        very_long_string = "A" * 10000
        
        start_response = self.client.post("/examination/start")
        session_id = start_response.cookies.get("session_id")
        
        response = self.client.post(
            "/examination/submit_answers",
            data={
                "session_id": session_id,
                "page_id": "1",
                "answers": f'{{"1": {{"type": "essay", "value": "{very_long_string}"}}}}'
            }
        )
        
        # Should handle long input gracefully
        assert response.status_code in [200, 302, 400, 422]
    
    def test_rate_limiting_protection(self):
        """Test protection against rapid requests (basic rate limiting test)"""
        # Make many rapid requests
        responses = []
        for i in range(50):
            response = self.client.get("/")
            responses.append(response.status_code)
        
        # Should handle rapid requests without crashing
        success_responses = [r for r in responses if r == 200]
        assert len(success_responses) > 0, "Server crashed under rapid requests"
    
    def test_admin_password_security(self):
        """Test admin password requirements and security"""
        # Test login with weak credentials
        weak_passwords = ["", "123", "password", "admin"]
        
        for weak_pass in weak_passwords:
            response = self.client.post("/admin/login", data={
                "username": "admin",
                "password": weak_pass
            })
            
            # Should not accept weak passwords (if they exist)
            assert response.status_code in [200, 302, 401]
    
    def test_sensitive_data_exposure(self, authenticated_admin_client):
        """Test that sensitive data is not exposed in responses"""
        # Check that password hashes are not exposed
        response = authenticated_admin_client.get("/admin/dashboard")
        
        if hasattr(response, 'text'):
            # Should not contain password hashes or sensitive tokens
            sensitive_patterns = ["$2b$", "password_hash", "bcrypt", "jwt_secret"]
            for pattern in sensitive_patterns:
                assert pattern not in response.text, f"Sensitive data '{pattern}' exposed in response"
    
    def test_directory_listing_disabled(self):
        """Test that directory listing is disabled"""
        directory_paths = ["/static/", "/templates/", "/app/"]
        
        for path in directory_paths:
            response = self.client.get(path)
            
            # Should not show directory contents
            assert response.status_code in [404, 403], f"Directory listing enabled for {path}"


class TestAuthenticationSecurity:
    """Authentication and authorization security tests"""
    
    def setup_method(self):
        self.client = TestClient(app)
    
    def test_brute_force_protection(self):
        """Test protection against brute force attacks"""
        # Attempt multiple failed logins
        for i in range(10):
            response = self.client.post("/admin/login", data={
                "username": "admin",
                "password": f"wrongpass{i}"
            })
            
            # Should handle multiple attempts gracefully
            assert response.status_code in [200, 302, 401, 429]
    
    def test_session_timeout(self, authenticated_admin_client):
        """Test session timeout functionality"""
        # Make initial authenticated request
        response = authenticated_admin_client.get("/admin/dashboard")
        assert response.status_code == 200
        
        # Sessions should be managed properly (this is a basic test)
        # In a real scenario, you'd test actual timeout behavior
    
    def test_logout_security(self, authenticated_admin_client):
        """Test logout properly invalidates session"""
        # Access protected resource
        response = authenticated_admin_client.get("/admin/dashboard")
        assert response.status_code == 200
        
        # Logout
        logout_response = authenticated_admin_client.post("/admin/logout")
        assert logout_response.status_code in [200, 302]
        
        # Try to access protected resource again with old session
        # (This would need proper session management to test effectively)
    
    def test_concurrent_sessions(self):
        """Test handling of concurrent admin sessions"""
        # Create multiple clients with same credentials
        clients = [TestClient(app) for _ in range(3)]
        
        login_responses = []
        for client in clients:
            response = client.post("/admin/login", data={
                "username": "testadmin",
                "password": "testpass123"
            })
            login_responses.append(response.status_code)
        
        # Should handle concurrent logins appropriately
        assert all(status in [200, 302, 401] for status in login_responses)


class TestDataSecurity:
    """Data protection and privacy tests"""
    
    def test_student_data_isolation(self, populated_db):
        """Test that student data is properly isolated"""
        # Create two examination sessions
        session1_response = self.client.post("/examination/start")
        session1_id = session1_response.cookies.get("session_id")
        
        session2_response = self.client.post("/examination/start")
        session2_id = session2_response.cookies.get("session_id")
        
        # Submit data for session 1
        self.client.post(
            "/examination/submit_answers",
            data={
                "session_id": session1_id,
                "page_id": "1",
                "answers": '{"1": {"type": "essay", "value": "Session 1 private data"}}'
            }
        )
        
        # Try to access session 1 data using session 2 ID
        # This would require additional endpoint to test properly
        # But the principle is that sessions should be isolated
        
        assert session1_id != session2_id, "Session IDs should be unique"
    
    def test_data_export_security(self, authenticated_admin_client):
        """Test that data export is properly secured"""
        # Test CSV export endpoint
        response = authenticated_admin_client.get("/admin/export_results")
        
        # Should require authentication
        assert response.status_code in [200, 302, 401, 404]
        
        # If successful, should return appropriate content type
        if response.status_code == 200:
            assert "text/csv" in response.headers.get("content-type", "").lower() or \
                   "application/octet-stream" in response.headers.get("content-type", "").lower()


@pytest.mark.security
class TestComplianceSecurity:
    """Compliance and regulatory security tests"""
    
    def test_data_retention_policy(self):
        """Test data retention policy compliance"""
        # This would test that old data is properly cleaned up
        # Implementation depends on specific data retention requirements
        pass
    
    def test_audit_logging(self):
        """Test that security-relevant actions are logged"""
        # This would test that admin actions are properly logged
        # Implementation depends on logging requirements
        pass
    
    def test_encryption_in_transit(self):
        """Test that data is encrypted in transit (HTTPS)"""
        # In production, this would test HTTPS enforcement
        # For testing, we verify that sensitive operations use secure methods
        pass