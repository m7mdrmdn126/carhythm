"""
Comprehensive integration tests for admin endpoints
Tests: login/logout, page CRUD, question CRUD (all types), results management
"""
import pytest
import json
from fastapi import status
from app.models import Admin, Page, Question, StudentResponse, QuestionAnswer, QuestionType


class TestAdminAuthentication:
    """Test admin login and authentication"""
    
    def test_admin_login_page_accessible(self, client):
        """Test admin login page is accessible"""
        response = client.get("/admin/login")
        
        assert response.status_code == 200
        assert b"login" in response.content.lower()
    
    def test_admin_login_success(self, client, test_admin):
        """Test successful admin login"""
        response = client.post("/admin/login", data={
            "username": "testadmin",
            "password": "testpass123"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/dashboard"
        assert "access_token" in response.cookies
    
    def test_admin_login_wrong_password(self, client, test_admin):
        """Test login with wrong password"""
        response = client.post("/admin/login", data={
            "username": "testadmin",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 200
        assert b"Invalid" in response.content or b"invalid" in response.content
    
    def test_admin_login_nonexistent_user(self, client):
        """Test login with nonexistent user"""
        response = client.post("/admin/login", data={
            "username": "nonexistent",
            "password": "anypassword"
        })
        
        assert response.status_code == 200
        assert b"Invalid" in response.content or b"invalid" in response.content
    
    def test_admin_logout(self, authenticated_admin_client):
        """Test admin logout"""
        response = authenticated_admin_client.get("/admin/logout", follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/login"
        # Cookie should be deleted
        assert "access_token" not in response.cookies or response.cookies["access_token"] == ""
    
    def test_dashboard_requires_authentication(self, client):
        """Test dashboard requires authentication"""
        response = client.get("/admin/dashboard", follow_redirects=False)
        
        assert response.status_code == 401
    
    def test_dashboard_accessible_when_authenticated(self, authenticated_admin_client):
        """Test authenticated admin can access dashboard"""
        response = authenticated_admin_client.get("/admin/dashboard")
        
        assert response.status_code == 200
        assert b"dashboard" in response.content.lower()


class TestPageCRUD:
    """Test page CRUD operations"""
    
    def test_view_pages(self, authenticated_admin_client):
        """Test viewing pages list"""
        response = authenticated_admin_client.get("/admin/pages")
        
        assert response.status_code == 200
        assert b"pages" in response.content.lower()
    
    def test_create_page(self, authenticated_admin_client):
        """Test creating a new page"""
        response = authenticated_admin_client.post("/admin/pages", data={
            "title": "New Test Page",
            "description": "A test page description",
            "order_index": "5"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/pages"
    
    def test_create_page_minimal_data(self, authenticated_admin_client):
        """Test creating page with minimal data"""
        response = authenticated_admin_client.post("/admin/pages", data={
            "title": "Minimal Page",
            "description": "",
            "order_index": "0"
        }, follow_redirects=False)
        
        assert response.status_code == 302
    
    def test_update_page(self, authenticated_admin_client, test_page, db_session):
        """Test updating an existing page"""
        response = authenticated_admin_client.post(f"/admin/pages/{test_page.id}/edit", data={
            "title": "Updated Page Title",
            "description": "Updated description",
            "order_index": "10",
            "is_active": "on"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify update
        db_session.refresh(test_page)
        assert test_page.title == "Updated Page Title"
        assert test_page.is_active is True
    
    def test_update_page_deactivate(self, authenticated_admin_client, test_page, db_session):
        """Test deactivating a page"""
        response = authenticated_admin_client.post(f"/admin/pages/{test_page.id}/edit", data={
            "title": test_page.title,
            "description": test_page.description or "",
            "order_index": str(test_page.order_index),
            # is_active not included = False
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        db_session.refresh(test_page)
        assert test_page.is_active is False
    
    def test_delete_page(self, authenticated_admin_client, test_page, db_session):
        """Test deleting a page"""
        page_id = test_page.id
        
        response = authenticated_admin_client.post(f"/admin/pages/{page_id}/delete", follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify deletion
        from app.models import Page
        deleted_page = db_session.query(Page).filter(Page.id == page_id).first()
        assert deleted_page is None


class TestQuestionCRUD:
    """Test question CRUD operations (all types)"""
    
    def test_view_questions(self, authenticated_admin_client, test_page):
        """Test viewing questions list"""
        response = authenticated_admin_client.get(f"/admin/questions?page_id={test_page.id}")
        
        assert response.status_code == 200
        assert b"questions" in response.content.lower()
    
    def test_create_essay_question(self, authenticated_admin_client, test_page):
        """Test creating essay question"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            "question_text": "What are your career goals?",
            "question_type": "essay",
            "order_index": "0",
            "is_required": "on",
            "essay_char_limit": "500",
            "slider_min_label": "",
            "slider_max_label": "",
            "randomize_order": "on"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert f"page_id={test_page.id}" in response.headers["location"]
    
    def test_create_slider_question(self, authenticated_admin_client, test_page):
        """Test creating slider question"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            "question_text": "Rate your interest in leadership",
            "question_type": "slider",
            "order_index": "1",
            "is_required": "on",
            "slider_min_label": "Not interested",
            "slider_max_label": "Very interested",
            "essay_char_limit": "",
            "randomize_order": "on"
        }, follow_redirects=False)
        
        assert response.status_code == 302
    
    def test_create_mcq_question(self, authenticated_admin_client, test_page):
        """Test creating MCQ question"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            "question_text": "What is your preferred work schedule?",
            "question_type": "mcq",
            "order_index": "2",
            "is_required": "on",
            "mcq_option": ["9-5 weekdays", "Flexible hours", "Remote work"],
            "mcq_correct": ["0"],
            "allow_multiple_selection": "off",
            "slider_min_label": "",
            "slider_max_label": "",
            "essay_char_limit": "",
            "randomize_order": "on"
        }, follow_redirects=False)
        
        assert response.status_code == 302
    
    def test_create_mcq_multiple_selection(self, authenticated_admin_client, test_page):
        """Test creating MCQ question with multiple selection"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            "question_text": "Which skills do you have?",
            "question_type": "mcq",
            "order_index": "3",
            "is_required": "on",
            "mcq_option": ["Communication", "Leadership", "Technical", "Creative"],
            "mcq_correct": ["0", "2"],
            "allow_multiple_selection": "on",
            "slider_min_label": "",
            "slider_max_label": "",
            "essay_char_limit": "",
            "randomize_order": "on"
        }, follow_redirects=False)
        
        assert response.status_code == 302
    
    def test_create_ordering_question(self, authenticated_admin_client, test_page):
        """Test creating ordering question"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            "question_text": "Rank these career factors",
            "question_type": "ordering",
            "order_index": "4",
            "is_required": "on",
            "ordering_option": ["Salary", "Work-Life Balance", "Career Growth", "Job Security"],
            "randomize_order": "on",
            "slider_min_label": "",
            "slider_max_label": "",
            "essay_char_limit": ""
        }, follow_redirects=False)
        
        assert response.status_code == 302
    
    def test_update_question(self, authenticated_admin_client, test_essay_question, db_session):
        """Test updating a question"""
        response = authenticated_admin_client.post(f"/admin/questions/{test_essay_question.id}/edit", data={
            "question_text": "Updated question text",
            "question_type": "essay",
            "order_index": "5",
            "is_required": "on",
            "essay_char_limit": "600",
            "slider_min_label": "",
            "slider_max_label": "",
            "remove_image": "off"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify update
        db_session.refresh(test_essay_question)
        assert test_essay_question.question_text == "Updated question text"
        assert test_essay_question.essay_char_limit == 600
    
    def test_delete_question(self, authenticated_admin_client, test_essay_question, db_session):
        """Test deleting a question"""
        question_id = test_essay_question.id
        
        response = authenticated_admin_client.post(f"/admin/questions/{question_id}/delete", follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify deletion
        deleted = db_session.query(Question).filter(Question.id == question_id).first()
        assert deleted is None
    
    def test_create_mcq_insufficient_options(self, authenticated_admin_client, test_page):
        """Test creating MCQ with less than 2 options"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            "question_text": "Invalid MCQ",
            "question_type": "mcq",
            "order_index": "0",
            "mcq_option": ["Only one option"],
            "mcq_correct": ["0"],
            "is_required": "on",
            "slider_min_label": "",
            "slider_max_label": "",
            "essay_char_limit": "",
            "randomize_order": "on"
        })
        
        assert response.status_code == 400
    
    def test_create_mcq_no_correct_answer(self, authenticated_admin_client, test_page):
        """Test creating MCQ without correct answer"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            "question_text": "MCQ without correct answer",
            "question_type": "mcq",
            "order_index": "0",
            "mcq_option": ["Option 1", "Option 2"],
            "mcq_correct": [],  # No correct answer
            "is_required": "on",
            "slider_min_label": "",
            "slider_max_label": "",
            "essay_char_limit": "",
            "randomize_order": "on"
        })
        
        assert response.status_code == 400


class TestResultsManagement:
    """Test viewing and managing student results"""
    
    def test_view_results_page(self, authenticated_admin_client):
        """Test viewing results page"""
        response = authenticated_admin_client.get("/admin/results")
        
        assert response.status_code == 200
        assert b"results" in response.content.lower() or b"responses" in response.content.lower()
    
    def test_view_results_with_responses(self, authenticated_admin_client, test_student_response):
        """Test viewing results with student responses"""
        response = authenticated_admin_client.get("/admin/results")
        
        assert response.status_code == 200
        # Should contain student email
        assert test_student_response.email.encode() in response.content
    
    def test_view_response_detail(self, authenticated_admin_client, test_student_response, test_question_answers):
        """Test viewing detailed response"""
        response = authenticated_admin_client.get(f"/admin/results/{test_student_response.id}")
        
        assert response.status_code == 200
        # Should contain student info
        assert test_student_response.full_name.encode() in response.content
    
    def test_view_nonexistent_response(self, authenticated_admin_client):
        """Test viewing nonexistent response"""
        response = authenticated_admin_client.get("/admin/results/99999")
        
        assert response.status_code == 404
    
    def test_delete_response(self, authenticated_admin_client, test_student_response, db_session):
        """Test deleting a response"""
        response_id = test_student_response.id
        
        response = authenticated_admin_client.post(f"/admin/results/{response_id}/delete", follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/results"
        
        # Verify deletion
        deleted = db_session.query(StudentResponse).filter(StudentResponse.id == response_id).first()
        assert deleted is None


class TestAdminAuthorization:
    """Test authorization for admin endpoints"""
    
    def test_pages_requires_auth(self, client):
        """Test pages endpoint requires authentication"""
        response = client.get("/admin/pages")
        
        assert response.status_code == 401
    
    def test_questions_requires_auth(self, client):
        """Test questions endpoint requires authentication"""
        response = client.get("/admin/questions")
        
        assert response.status_code == 401
    
    def test_results_requires_auth(self, client):
        """Test results endpoint requires authentication"""
        response = client.get("/admin/results")
        
        assert response.status_code == 401
    
    def test_create_page_requires_auth(self, client):
        """Test creating page requires authentication"""
        response = client.post("/admin/pages", data={
            "title": "Test Page",
            "description": "Test",
            "order_index": "0"
        })
        
        assert response.status_code == 401
    
    def test_delete_page_requires_auth(self, client, test_page):
        """Test deleting page requires authentication"""
        response = client.post(f"/admin/pages/{test_page.id}/delete")
        
        assert response.status_code == 401


class TestAdminWorkflow:
    """Test complete admin workflows"""
    
    def test_complete_page_creation_workflow(self, authenticated_admin_client, db_session):
        """Test complete workflow: create page -> add questions -> verify"""
        # Step 1: Create page
        response = authenticated_admin_client.post("/admin/pages", data={
            "title": "Workflow Test Page",
            "description": "Testing complete workflow",
            "order_index": "0"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Get the created page
        from app.models import Page
        page = db_session.query(Page).filter(Page.title == "Workflow Test Page").first()
        assert page is not None
        
        # Step 2: Add essay question
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(page.id),
            "question_text": "Essay question",
            "question_type": "essay",
            "order_index": "0",
            "is_required": "on",
            "essay_char_limit": "500",
            "slider_min_label": "",
            "slider_max_label": "",
            "randomize_order": "on"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Step 3: Add slider question
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(page.id),
            "question_text": "Slider question",
            "question_type": "slider",
            "order_index": "1",
            "is_required": "on",
            "slider_min_label": "Low",
            "slider_max_label": "High",
            "essay_char_limit": "",
            "randomize_order": "on"
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # Step 4: Verify questions were created
        questions = db_session.query(Question).filter(Question.page_id == page.id).all()
        assert len(questions) == 2
    
    def test_update_page_with_questions(self, authenticated_admin_client, test_page, test_essay_question, db_session):
        """Test updating page that has questions"""
        # Update page
        response = authenticated_admin_client.post(f"/admin/pages/{test_page.id}/edit", data={
            "title": "Updated Page With Questions",
            "description": "Updated description",
            "order_index": "5",
            "is_active": "on"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify page updated
        db_session.refresh(test_page)
        assert test_page.title == "Updated Page With Questions"
        
        # Verify question still exists
        db_session.refresh(test_essay_question)
        assert test_essay_question.page_id == test_page.id
    
    def test_delete_page_cascades_questions(self, authenticated_admin_client, test_page, test_essay_question, db_session):
        """Test deleting page also deletes its questions"""
        question_id = test_essay_question.id
        page_id = test_page.id
        
        # Delete page
        response = authenticated_admin_client.post(f"/admin/pages/{page_id}/delete", follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify page deleted
        deleted_page = db_session.query(Page).filter(Page.id == page_id).first()
        assert deleted_page is None
        
        # Verify question also deleted (cascade)
        deleted_question = db_session.query(Question).filter(Question.id == question_id).first()
        assert deleted_question is None
