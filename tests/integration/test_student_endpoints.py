import pytest
from fastapi import status
import json


class TestStudentJourney:
    """Test complete student examination journey"""
    
    def test_welcome_page(self, client):
        """Test student welcome page"""
        response = client.get("/student/welcome")
        assert response.status_code == status.HTTP_200_OK
        assert "Welcome to Career DNA Assessment" in response.text
        assert "Start Assessment" in response.text
    
    def test_root_redirect_to_welcome(self, client):
        """Test root URL redirects to welcome"""
        response = client.get("/")
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/student/welcome"
    
    def test_exam_start_with_no_pages(self, client):
        """Test exam start when no pages exist"""
        response = client.get("/student/exam")
        assert response.status_code == status.HTTP_200_OK
        assert "No examination pages available" in response.text
    
    def test_exam_start_with_pages(self, client, test_page, test_essay_question):
        """Test exam start with available pages"""
        response = client.get("/student/exam")
        assert response.status_code == status.HTTP_200_OK
        assert test_page.title in response.text
        assert test_essay_question.question_text in response.text
        
        # Should set session cookie
        assert "session_id" in response.cookies
    
    def test_exam_navigation(self, client, test_page, test_essay_question):
        """Test exam page navigation"""
        # Start exam to get session
        start_response = client.get("/student/exam")
        session_id = start_response.cookies["session_id"]
        
        # Navigate to specific page
        response = client.get(f"/student/exam/page/0")
        assert response.status_code == status.HTTP_200_OK
        assert test_page.title in response.text
    
    def test_invalid_page_number(self, client, test_page):
        """Test navigation to invalid page number"""
        response = client.get("/student/exam/page/999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_submit_answers(self, client, test_page, test_essay_question, test_slider_question):
        """Test answer submission"""
        # Start exam to get session
        start_response = client.get("/student/exam")
        session_id = start_response.cookies["session_id"]
        
        # Submit answers
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_essay_question.id}_text": "My career goal is to become a data scientist.",
            f"question_{test_slider_question.id}_slider": "75"
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        # Verify response contains success status
        response_data = response.json()
        assert response_data["status"] == "success"
    
    def test_student_info_page(self, client):
        """Test student information page"""
        response = client.get("/student/info")
        assert response.status_code == status.HTTP_200_OK
        assert "Almost Done!" in response.text
        assert "Full Name" in response.text
        assert "Email Address" in response.text
    
    def test_submit_student_info(self, client, sample_student_data):
        """Test student information submission"""
        # Create a session first
        start_response = client.get("/student/exam")
        session_id = start_response.cookies["session_id"]
        
        # Submit student info
        response = client.post("/student/info", data={
            "session_id": session_id,
            **sample_student_data
        })
        
        # Should redirect to completion page
        assert response.status_code == status.HTTP_302_FOUND
        assert response.headers["location"] == "/student/completion"
    
    def test_completion_page(self, client):
        """Test assessment completion page"""
        response = client.get("/student/completion")
        assert response.status_code == status.HTTP_200_OK
        assert "Assessment Complete!" in response.text
        assert "Thank you for completing" in response.text


class TestExaminationFlow:
    """Test examination flow with multiple pages"""
    
    def setup_method(self):
        """Setup test data for examination flow"""
        self.session_data = None
    
    def test_multi_page_examination(self, client, db_session, sample_questions_data):
        """Test complete multi-page examination flow"""
        from app.models import Page, Question, QuestionType
        from app.services.question_service import create_page, create_question
        from app.schemas import PageCreate, QuestionCreate
        
        # Create multiple pages with questions
        page1 = create_page(db_session, PageCreate(title="Page 1", order_index=0))
        page2 = create_page(db_session, PageCreate(title="Page 2", order_index=1))
        
        # Add questions to pages
        q1 = create_question(db_session, QuestionCreate(
            page_id=page1.id,
            question_text="Question 1",
            question_type=QuestionType.essay,
            order_index=0
        ))
        q2 = create_question(db_session, QuestionCreate(
            page_id=page2.id,
            question_text="Question 2",
            question_type=QuestionType.slider,
            order_index=0,
            slider_min_label="Low",
            slider_max_label="High"
        ))
        
        # Start examination
        start_response = client.get("/student/exam")
        assert start_response.status_code == status.HTTP_200_OK
        session_id = start_response.cookies["session_id"]
        
        # Page 1
        page1_response = client.get("/student/exam/page/0")
        assert page1_response.status_code == status.HTTP_200_OK
        assert "Page 1 of 2" in page1_response.text
        
        # Submit answers for page 1
        client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{q1.id}_text": "Answer to question 1"
        })
        
        # Page 2
        page2_response = client.get("/student/exam/page/1")
        assert page2_response.status_code == status.HTTP_200_OK
        assert "Page 2 of 2" in page2_response.text
        
        # Submit answers for page 2
        client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{q2.id}_slider": "80"
        })
        
        # Complete with student info
        completion_response = client.post("/student/info", data={
            "session_id": session_id,
            "email": "test@complete.com",
            "full_name": "Complete Test",
            "age_group": "23-25",
            "country": "USA",
            "origin_country": "USA"
        })
        
        assert completion_response.status_code == status.HTTP_302_FOUND


class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_submit_single_answer_api(self, client, test_page, test_essay_question):
        """Test single answer submission API"""
        # Start exam to get session
        start_response = client.get("/student/exam")
        session_id = start_response.cookies["session_id"]
        
        # Submit single answer via API
        response = client.post("/api/submit-answer", data={
            "session_id": session_id,
            "question_id": test_essay_question.id,
            "answer_text": "API submitted answer",
            "answer_value": None
        })
        
        assert response.status_code == status.HTTP_200_OK
        
        data = response.json()
        assert data["status"] == "success"


class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_session_id(self, client):
        """Test handling of invalid session ID"""
        response = client.post("/student/exam/submit-answers", data={
            "session_id": "invalid-session-id",
            "question_1_text": "Some answer"
        })
        
        # Should still work as it creates temporary response
        assert response.status_code == status.HTTP_200_OK
    
    def test_missing_session_id(self, client):
        """Test handling of missing session ID"""
        response = client.post("/student/exam/submit-answers", data={
            "question_1_text": "Some answer"
        })
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_nonexistent_response_detail(self, authenticated_admin_client):
        """Test accessing non-existent response detail"""
        response = authenticated_admin_client.get("/admin/results/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_nonexistent_page_navigation(self, client):
        """Test navigating to non-existent page"""
        response = client.get("/student/exam/page/-1")
        assert response.status_code == status.HTTP_404_NOT_FOUND