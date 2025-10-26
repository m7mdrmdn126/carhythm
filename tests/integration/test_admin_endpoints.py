import pytest
from fastapi import status


class TestAdminAuthentication:
    """Test admin authentication endpoints"""
    
    def test_admin_login_page(self, client):
        """Test admin login page loads"""
        response = client.get("/admin/login")
        assert response.status_code == status.HTTP_200_OK
        assert "Admin Login" in response.text
    
    def test_admin_login_success(self, client, test_admin):
        """Test successful admin login"""
        response = client.post("/admin/login", data={
            "username": test_admin.username,
            "password": "testpass123"
        })
        
        # Should redirect to dashboard
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/admin/dashboard"
        
        # Should set authentication cookie
        assert "access_token" in response.cookies
    
    def test_admin_login_failure(self, client, test_admin):
        """Test failed admin login"""
        response = client.post("/admin/login", data={
            "username": test_admin.username,
            "password": "wrongpassword"
        })
        
        # Should stay on login page with error
        assert response.status_code == status.HTTP_200_OK
        assert "Invalid username or password" in response.text
    
    def test_admin_dashboard_requires_auth(self, client):
        """Test dashboard requires authentication"""
        response = client.get("/admin/dashboard")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_admin_dashboard_with_auth(self, authenticated_admin_client):
        """Test dashboard with authentication"""
        response = authenticated_admin_client.get("/admin/dashboard")
        assert response.status_code == status.HTTP_200_OK
        assert "Admin Dashboard" in response.text
    
    def test_admin_logout(self, authenticated_admin_client):
        """Test admin logout"""
        response = authenticated_admin_client.get("/admin/logout")
        
        # Should redirect to login page
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/admin/login"
        
        # Should clear authentication cookie
        assert response.cookies.get("access_token") == ""


class TestPageManagement:
    """Test page management endpoints"""
    
    def test_pages_list_requires_auth(self, client):
        """Test pages list requires authentication"""
        response = client.get("/admin/pages")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_pages_list_with_auth(self, authenticated_admin_client, test_page):
        """Test pages list with authentication"""
        response = authenticated_admin_client.get("/admin/pages")
        assert response.status_code == status.HTTP_200_OK
        assert "Manage Pages" in response.text
        assert test_page.title in response.text
    
    def test_create_page(self, authenticated_admin_client):
        """Test page creation"""
        response = authenticated_admin_client.post("/admin/pages", data={
            "title": "New Test Page",
            "description": "A page created during testing",
            "order_index": 1
        })
        
        # Should redirect back to pages list
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/admin/pages"
    
    def test_update_page(self, authenticated_admin_client, test_page):
        """Test page update"""
        response = authenticated_admin_client.post(f"/admin/pages/{test_page.id}/edit", data={
            "title": "Updated Page Title",
            "description": "Updated description",
            "order_index": 2,
            "is_active": "true"
        })
        
        # Should redirect back to pages list
        assert response.status_code == status.HTTP_302_FOUND
    
    def test_delete_page(self, authenticated_admin_client, test_page):
        """Test page deletion"""
        response = authenticated_admin_client.post(f"/admin/pages/{test_page.id}/delete")
        
        # Should redirect back to pages list
        assert response.status_code == status.HTTP_302_FOUND


class TestQuestionManagement:
    """Test question management endpoints"""
    
    def test_questions_list_requires_auth(self, client):
        """Test questions list requires authentication"""
        response = client.get("/admin/questions")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_questions_list_with_auth(self, authenticated_admin_client, test_page):
        """Test questions list with authentication"""
        response = authenticated_admin_client.get(f"/admin/questions?page_id={test_page.id}")
        assert response.status_code == status.HTTP_200_OK
        assert "Manage Questions" in response.text
    
    def test_create_essay_question(self, authenticated_admin_client, test_page):
        """Test essay question creation"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": test_page.id,
            "question_text": "What are your career aspirations?",
            "question_type": "essay",
            "order_index": 1,
            "is_required": "true",
            "essay_char_limit": 300
        })
        
        # Should redirect back to questions page
        assert response.status_code == status.HTTP_302_FOUND
    
    def test_create_slider_question(self, authenticated_admin_client, test_page):
        """Test slider question creation"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": test_page.id,
            "question_text": "Rate your interest in teamwork",
            "question_type": "slider",
            "order_index": 2,
            "is_required": "true",
            "slider_min_label": "Not interested",
            "slider_max_label": "Very interested"
        })
        
        # Should redirect back to questions page
        assert response.status_code == status.HTTP_302_FOUND
    
    def test_delete_question(self, authenticated_admin_client, test_essay_question):
        """Test question deletion"""
        response = authenticated_admin_client.post(f"/admin/questions/{test_essay_question.id}/delete")
        
        # Should redirect back to questions page
        assert response.status_code == status.HTTP_302_FOUND


class TestResultsManagement:
    """Test results management endpoints"""
    
    def test_results_list_requires_auth(self, client):
        """Test results list requires authentication"""
        response = client.get("/admin/results")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_results_list_with_auth(self, authenticated_admin_client, test_student_response):
        """Test results list with authentication"""
        response = authenticated_admin_client.get("/admin/results")
        assert response.status_code == status.HTTP_200_OK
        assert "Assessment Results" in response.text
    
    def test_results_detail(self, authenticated_admin_client, test_student_response):
        """Test individual result detail"""
        response = authenticated_admin_client.get(f"/admin/results/{test_student_response.id}")
        assert response.status_code == status.HTTP_200_OK
        assert test_student_response.full_name in response.text
    
    def test_delete_response(self, authenticated_admin_client, test_student_response):
        """Test response deletion"""
        response = authenticated_admin_client.post(f"/admin/results/{test_student_response.id}/delete")
        
        # Should redirect back to results list
        assert response.status_code == status.HTTP_302_FOUND