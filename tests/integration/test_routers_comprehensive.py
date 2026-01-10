"""
Comprehensive integration tests for all router endpoints
Tests the full API workflow including admin panel, student examination, feedback, and question pools
"""

import pytest
import json
from fastapi import status
from io import BytesIO


class TestAdminAuthentication:
    """Test admin authentication endpoints"""
    
    def test_login_success(self, client, test_admin):
        """Test successful admin login"""
        response = client.post("/admin/login", data={
            "username": "testadmin",
            "password": "testpass123"
        }, follow_redirects=False)
        assert response.status_code == 302  # Redirect to dashboard
        assert response.headers.get("location") == "/admin/dashboard"
    
    def test_login_invalid_credentials(self, client, test_admin):
        """Test login with invalid credentials"""
        response = client.post("/admin/login", data={
            "username": "testadmin",
            "password": "wrongpassword"
        }, follow_redirects=False)
        assert response.status_code == 200  # Returns login page with error
    
    def test_login_nonexistent_user(self, client):
        """Test login with non-existent user"""
        response = client.post("/admin/login", data={
            "username": "nonexistent",
            "password": "password123"
        }, follow_redirects=False)
        assert response.status_code == 200  # Returns login page with error
    
    def test_logout(self, authenticated_admin_client):
        """Test admin logout"""
        response = authenticated_admin_client.get("/admin/logout", follow_redirects=False)
        assert response.status_code == 302
    
    def test_dashboard_requires_auth(self, client):
        """Test that dashboard requires authentication"""
        response = client.get("/admin/dashboard", follow_redirects=False)
        assert response.status_code in [302, 401]  # Redirect to login or Unauthorized

class TestPageManagement:
    """Test page CRUD operations"""
    
    def test_get_pages_list(self, authenticated_admin_client):
        """Test retrieving pages list"""
        response = authenticated_admin_client.get("/admin/pages")
        assert response.status_code == 200
    
    def test_create_page(self, authenticated_admin_client, db_session):
        """Test creating a new page"""
        response = authenticated_admin_client.post("/admin/pages", data={
            "title": "New Assessment Page",
            "description": "A new page for testing",
            "order_index": "5",
            "emoji": "📝",
            "is_active": "true"
        })
        assert response.status_code == 302  # Redirect after creation
        
        # Verify in database
        from app.models import Page
        page = db_session.query(Page).filter(Page.title == "New Assessment Page").first()
        assert page is not None
        assert page.description == "A new page for testing"
    
    def test_update_page(self, authenticated_admin_client, test_page, db_session):
        """Test updating a page"""
        response = authenticated_admin_client.post(f"/admin/pages/{test_page.id}/edit", data={
            "title": "Updated Page Title",
            "description": "Updated description",
            "order_index": "2",
            "is_active": "true"
        })
        assert response.status_code == 302
        
        # Verify update
        db_session.refresh(test_page)
        assert test_page.title == "Updated Page Title"
    
    def test_delete_page(self, authenticated_admin_client, test_page, db_session):
        """Test deleting a page"""
        page_id = test_page.id
        response = authenticated_admin_client.post(f"/admin/pages/{page_id}/delete")
        assert response.status_code == 302
        
        # Verify deletion
        from app.models import Page
        page = db_session.query(Page).filter(Page.id == page_id).first()
        assert page is None
    
    def test_update_page_order(self, authenticated_admin_client, multiple_pages):
        """Test updating page order"""
        new_order = [{"id": p.id, "order_index": i} for i, p in enumerate(reversed(multiple_pages))]
        response = authenticated_admin_client.post("/admin/pages/update-order",
            json=new_order,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200


class TestQuestionManagement:
    """Test question CRUD operations"""
    
    def test_get_questions_list(self, authenticated_admin_client):
        """Test retrieving questions list"""
        response = authenticated_admin_client.get("/admin/questions")
        assert response.status_code == 200
    
    def test_create_essay_question(self, authenticated_admin_client, test_page, db_session):
        """Test creating an essay question"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            "question_text": "What motivates you in your career?",
            "question_type": "essay",
            "order_index": "1",
            "is_required": "true",
            "essay_char_limit": "300"
        })
        assert response.status_code == 302
        
        from app.models import Question
        question = db_session.query(Question).filter(
            Question.question_text == "What motivates you in your career?"
        ).first()
        assert question is not None
        assert question.question_type.value == "essay"
    
    def test_create_slider_question(self, authenticated_admin_client, test_page, db_session):
        """Test creating a slider question"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            "question_text": "Rate your problem-solving skills",
            "question_type": "slider",
            "order_index": "2",
            "is_required": "true",
            "slider_min_label": "Poor",
            "slider_max_label": "Excellent"
        })
        assert response.status_code == 302
    
    def test_create_mcq_question(self, authenticated_admin_client, test_page, db_session):
        """Test creating an MCQ question"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            "question_text": "What is your work style?",
            "question_type": "mcq",
            "order_index": "3",
            "is_required": "true",
            "mcq_options": json.dumps(["Independent", "Collaborative", "Flexible", "Structured"]),
            "mcq_correct_answer": json.dumps([0]),
            "allow_multiple_selection": "false"
        })
        assert response.status_code == 302
    
    def test_update_question(self, authenticated_admin_client, test_essay_question, db_session):
        """Test updating a question"""
        response = authenticated_admin_client.post(f"/admin/questions/{test_essay_question.id}/edit", data={
            "page_id": str(test_essay_question.page_id),
            "question_text": "Updated question text",
            "question_type": "essay",
            "order_index": "1",
            "is_required": "true",
            "essay_char_limit": "500"
        })
        assert response.status_code == 302
        
        db_session.refresh(test_essay_question)
        assert test_essay_question.question_text == "Updated question text"
    
    def test_delete_question(self, authenticated_admin_client, test_essay_question, db_session):
        """Test deleting a question"""
        question_id = test_essay_question.id
        response = authenticated_admin_client.post(f"/admin/questions/{question_id}/delete")
        assert response.status_code == 302
        
        from app.models import Question
        question = db_session.query(Question).filter(Question.id == question_id).first()
        assert question is None
    
    def test_get_question_data_api(self, authenticated_admin_client, test_essay_question):
        """Test getting question data via API"""
        response = authenticated_admin_client.get(f"/admin/questions/{test_essay_question.id}/data")
        assert response.status_code == 200
        data = response.json()
        assert data["question_text"] == test_essay_question.question_text


class TestResponseManagement:
    """Test student response management"""
    
    def test_get_responses_list(self, authenticated_admin_client):
        """Test retrieving responses list"""
        response = authenticated_admin_client.get("/admin/results")
        assert response.status_code == 200
    
    def test_view_single_response(self, authenticated_admin_client, test_student_response):
        """Test viewing a single response"""
        response = authenticated_admin_client.get(f"/admin/results/{test_student_response.id}")
        assert response.status_code == 200
    
    def test_delete_response(self, authenticated_admin_client, test_student_response, db_session):
        """Test deleting a response"""
        response_id = test_student_response.id
        response = authenticated_admin_client.post(f"/admin/results/{response_id}/delete")
        assert response.status_code == 302
        
        from app.models import StudentResponse
        resp = db_session.query(StudentResponse).filter(StudentResponse.id == response_id).first()
        assert resp is None
    
    def test_bulk_delete_responses(self, authenticated_admin_client, db_session, test_student_response):
        """Test bulk deleting responses"""
        response = authenticated_admin_client.post("/admin/results/bulk-delete",
            json={"response_ids": [test_student_response.id]},
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
    
    def test_export_response_csv(self, authenticated_admin_client, test_student_response):
        """Test exporting response as CSV"""
        response = authenticated_admin_client.get(f"/admin/results/{test_student_response.id}/export/csv")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")


class TestCategoryManagement:
    """Test category CRUD operations"""
    
    def test_get_categories_list(self, authenticated_admin_client):
        """Test retrieving categories list"""
        response = authenticated_admin_client.get("/admin/categories")
        assert response.status_code == 200
    
    def test_create_category(self, authenticated_admin_client, db_session):
        """Test creating a category"""
        response = authenticated_admin_client.post("/admin/categories", data={
            "name": "Personality Tests",
            "description": "Questions assessing personality traits",
            "color": "#9b59b6"
        })
        assert response.status_code == 302
        
        from app.models import Category
        category = db_session.query(Category).filter(Category.name == "Personality Tests").first()
        assert category is not None
        assert category.color == "#9b59b6"
    
    def test_update_category(self, authenticated_admin_client, test_category, db_session):
        """Test updating a category"""
        response = authenticated_admin_client.post(f"/admin/categories/{test_category.id}/edit", data={
            "name": "Updated Category",
            "description": "Updated description",
            "color": "#e74c3c",
            "is_active": "true"
        })
        assert response.status_code == 302
        
        db_session.refresh(test_category)
        assert test_category.name == "Updated Category"
    
    def test_delete_category(self, authenticated_admin_client, db_session):
        """Test deleting a category"""
        from app.models import Category
        category = Category(name="Temporary Category", color="#000000")
        db_session.add(category)
        db_session.commit()
        db_session.refresh(category)
        
        category_id = category.id
        response = authenticated_admin_client.post(f"/admin/categories/{category_id}/delete")
        assert response.status_code == 302


class TestQuestionPoolManagement:
    """Test question pool operations"""
    
    def test_get_question_pool_dashboard(self, authenticated_admin_client):
        """Test question pool dashboard"""
        response = authenticated_admin_client.get("/admin/question-pool")
        assert response.status_code == 200
    
    def test_create_pool_question(self, authenticated_admin_client, test_category, db_session):
        """Test creating a question in the pool"""
        response = authenticated_admin_client.post("/admin/question-pool/questions", data={
            "title": "Pool Question Title",
            "question_text": "This is a pool question",
            "question_type": "essay",
            "category_id": str(test_category.id),
            "is_required": "true",
            "essay_char_limit": "400"
        })
        assert response.status_code == 302
        
        from app.models import QuestionPool
        question = db_session.query(QuestionPool).filter(
            QuestionPool.title == "Pool Question Title"
        ).first()
        assert question is not None
    
    def test_update_pool_question(self, authenticated_admin_client, test_question_pool, db_session):
        """Test updating a pool question"""
        response = authenticated_admin_client.post(f"/admin/question-pool/questions/{test_question_pool.id}/edit", data={
            "title": "Updated Pool Question",
            "question_text": "Updated question text",
            "question_type": "essay",
            "category_id": str(test_question_pool.category_id),
            "is_required": "true",
            "essay_char_limit": "600"
        })
        assert response.status_code == 302
        
        db_session.refresh(test_question_pool)
        assert test_question_pool.title == "Updated Pool Question"
    
    def test_delete_pool_question(self, authenticated_admin_client, test_question_pool, db_session):
        """Test deleting a pool question"""
        question_id = test_question_pool.id
        response = authenticated_admin_client.post(f"/admin/question-pool/questions/{question_id}/delete")
        assert response.status_code == 302
        
        from app.models import QuestionPool
        question = db_session.query(QuestionPool).filter(QuestionPool.id == question_id).first()
        assert question is None
    
    def test_assign_question_to_page(self, authenticated_admin_client, test_question_pool, test_page, db_session):
        """Test assigning a pool question to a page"""
        response = authenticated_admin_client.post(f"/admin/pages/{test_page.id}/assign-question", data={
            "question_pool_id": str(test_question_pool.id),
            "order_index": "0"
        })
        assert response.status_code == 302
        
        from app.models import QuestionPageAssignment
        assignment = db_session.query(QuestionPageAssignment).filter(
            QuestionPageAssignment.question_pool_id == test_question_pool.id,
            QuestionPageAssignment.page_id == test_page.id
        ).first()
        assert assignment is not None
    
    def test_filter_questions_by_category(self, authenticated_admin_client, test_category):
        """Test filtering pool questions by category"""
        response = authenticated_admin_client.get(f"/admin/question-pool?category_id={test_category.id}")
        assert response.status_code == 200
    
    def test_filter_questions_by_type(self, authenticated_admin_client):
        """Test filtering pool questions by type"""
        response = authenticated_admin_client.get("/admin/question-pool?question_type=essay")
        assert response.status_code == 200
    
    def test_search_pool_questions(self, authenticated_admin_client):
        """Test searching pool questions"""
        response = authenticated_admin_client.get("/admin/question-pool?search=career")
        assert response.status_code == 200


class TestStudentExamination:
    """Test student examination workflow"""
    
    def test_get_welcome_page(self, client):
        """Test student welcome page"""
        response = client.get("/student/welcome")
        assert response.status_code == 200
    
    def test_start_exam(self, client):
        """Test starting an exam"""
        response = client.get("/student/exam")
        assert response.status_code == 200
    
    def test_get_exam_page(self, client, test_page):
        """Test getting a specific exam page"""
        # Start exam first to get session
        start_response = client.get("/student/exam")
        
        response = client.get(f"/student/exam/page/{test_page.order_index}")
        assert response.status_code in [200, 302]  # 200 OK or 302 redirect
    
    def test_submit_answers(self, client, test_page, test_essay_question, test_slider_question, db_session):
        """Test submitting answers for a page"""
        # Create a session
        from app.models import StudentResponse
        import uuid
        
        session_id = str(uuid.uuid4())
        student_response = StudentResponse(
            session_id=session_id,
            email="test@example.com",
            full_name="Test Student",
            age_group="19-22",
            country="USA",
            origin_country="USA"
        )
        db_session.add(student_response)
        db_session.commit()
        
        # Submit answers
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_essay_question.id}": "My career goal is to become a data scientist",
            f"question_{test_slider_question.id}": "75"
        })
        assert response.status_code in [200, 302]
    
    def test_complete_exam(self, client, test_student_response):
        """Test completing an exam"""
        response = client.post("/student/exam/complete", data={
            "session_id": test_student_response.session_id,
            "email": "test@example.com",
            "full_name": "Test Student",
            "age_group": "19-22",
            "country": "USA",
            "origin_country": "USA"
        })
        assert response.status_code in [200, 302]


class TestAPIv2Endpoints:
    """Test REST API v2 endpoints for React frontend"""
    
    def test_get_modules(self, client, test_page):
        """Test getting assessment modules"""
        response = client.get("/api/v2/modules")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_start_session(self, client):
        """Test starting a new session"""
        response = client.post("/api/v2/session/start")
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
    
    def test_get_questions(self, client, test_page, test_essay_question):
        """Test getting questions for a page"""
        response = client.get(f"/api/v2/questions?page_id={test_page.id}&language=en")
        assert response.status_code == 200
        data = response.json()
        assert "questions" in data
    
    def test_submit_answer(self, client, test_student_response, test_essay_question):
        """Test submitting an answer via API"""
        response = client.post("/api/v2/answers/submit", json={
            "session_id": test_student_response.session_id,
            "question_id": test_essay_question.id,
            "answer": {"text": "Test answer"}  # answer should be a dict
        })
        assert response.status_code in [200, 400]  # 200 success or 400 validation error
    
    def test_submit_student_info(self, client, test_student_response):
        """Test submitting student information"""
        response = client.post("/api/v2/student/info", json={
            "session_id": test_student_response.session_id,
            "email": "student@test.com",
            "full_name": "API Test Student",
            "age_group": "19-22",
            "country": "Canada",
            "origin_country": "India"
        })
        assert response.status_code in [200, 400]


class TestFeedbackEndpoints:
    """Test feedback system endpoints"""
    
    def test_submit_feedback(self, client, test_student_response):
        """Test submitting feedback"""
        response = client.post("/api/v2/feedback/submit", json={
            "session_id": test_student_response.session_id,
            "rating": 5,
            "experience_text": "Great assessment!"
        })
        assert response.status_code in [200, 201]
    
    def test_get_feedback_list(self, authenticated_admin_client):
        """Test getting feedback list (admin)"""
        response = authenticated_admin_client.get("/api/v2/feedback/list")
        assert response.status_code == 200


class TestAnalyticsEndpoints:
    """Test analytics and dashboard endpoints"""
    
    def test_get_dashboard(self, authenticated_admin_client):
        """Test admin dashboard"""
        response = authenticated_admin_client.get("/admin/dashboard")
        assert response.status_code == 200
    
    def test_get_analytics(self, authenticated_admin_client):
        """Test analytics page"""
        response = authenticated_admin_client.get("/admin/analytics")
        assert response.status_code == 200
    
    def test_get_analytics_data(self, authenticated_admin_client):
        """Test analytics data API"""
        response = authenticated_admin_client.get("/admin/analytics/data")
        assert response.status_code == 200
        data = response.json()
        assert "total_responses" in data or "statistics" in data


class TestCSVOperations:
    """Test CSV import/export operations"""
    
    def test_download_essay_template(self, authenticated_admin_client):
        """Test downloading CSV template for essay questions"""
        response = authenticated_admin_client.get("/admin/csv-templates/essay")
        assert response.status_code == 200
        assert "text/csv" in response.headers.get("content-type", "")
    
    def test_download_slider_template(self, authenticated_admin_client):
        """Test downloading CSV template for slider questions"""
        response = authenticated_admin_client.get("/admin/csv-templates/slider")
        assert response.status_code == 200
    
    def test_download_mcq_template(self, authenticated_admin_client):
        """Test downloading CSV template for MCQ questions"""
        response = authenticated_admin_client.get("/admin/csv-templates/mcq")
        assert response.status_code == 200
    
    def test_import_csv_questions(self, authenticated_admin_client, test_category):
        """Test importing questions from CSV"""
        csv_content = f"""title,question_text,category_name,is_required,essay_char_limit
Test Question,What are your goals?,{test_category.name},TRUE,500"""
        
        csv_file = BytesIO(csv_content.encode('utf-8'))
        csv_file.name = 'test_import.csv'
        
        response = authenticated_admin_client.post(
            "/admin/csv-import/essay",
            files={"csv_file": ("test.csv", csv_file, "text/csv")}
        )
        assert response.status_code in [200, 302]
    
    def test_export_questions_to_csv(self, authenticated_admin_client, test_question_pool):
        """Test exporting questions to CSV"""
        response = authenticated_admin_client.get(
            f"/admin/question-pool/export?question_ids={test_question_pool.id}&question_type=essay"
        )
        assert response.status_code == 200


class TestSettingsEndpoints:
    """Test settings and configuration endpoints"""
    
    def test_get_settings_page(self, authenticated_admin_client):
        """Test accessing settings page"""
        response = authenticated_admin_client.get("/admin/settings")
        assert response.status_code == 200
    
    def test_update_admin_password(self, authenticated_admin_client, test_admin, db_session):
        """Test updating admin password"""
        response = authenticated_admin_client.post("/admin/settings/password", data={
            "current_password": "testpass123",
            "new_password": "newpass123",
            "confirm_password": "newpass123"
        })
        assert response.status_code in [200, 302]
