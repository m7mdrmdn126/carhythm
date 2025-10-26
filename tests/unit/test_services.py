import pytest
from app.services.auth import authenticate_admin, create_admin, get_admin_by_username, login_admin
from app.services.question_service import (
    create_page, get_pages, get_page_by_id, update_page, delete_page,
    create_question, get_questions_by_page, get_question_by_id, update_question, delete_question
)
from app.services.response_service import (
    create_student_response, get_student_response_by_session, complete_student_response,
    create_question_answer, get_all_responses, get_response_statistics
)
from app.schemas import (
    AdminCreate, AdminLogin, PageCreate, PageUpdate, QuestionCreate, QuestionUpdate,
    StudentResponseCreate, QuestionAnswerCreate
)
from app.models import QuestionType


class TestAuthService:
    """Test authentication service functions"""
    
    def test_create_admin(self, db_session):
        """Test admin creation service"""
        admin_data = AdminCreate(username="newadmin", password="password123")
        admin = create_admin(db_session, admin_data)
        
        assert admin.id is not None
        assert admin.username == "newadmin"
        # Password should be hashed, not plain text
        assert admin.password_hash != "password123"
    
    def test_get_admin_by_username(self, db_session, test_admin):
        """Test getting admin by username"""
        admin = get_admin_by_username(db_session, test_admin.username)
        assert admin is not None
        assert admin.id == test_admin.id
        
        # Test non-existent admin
        non_existent = get_admin_by_username(db_session, "nonexistent")
        assert non_existent is None
    
    def test_authenticate_admin(self, db_session, test_admin):
        """Test admin authentication"""
        # Test correct credentials
        authenticated = authenticate_admin(db_session, test_admin.username, "testpass123")
        assert authenticated is not None
        assert authenticated.id == test_admin.id
        
        # Test wrong password
        wrong_pass = authenticate_admin(db_session, test_admin.username, "wrongpass")
        assert wrong_pass is None
        
        # Test non-existent user
        non_existent = authenticate_admin(db_session, "nonexistent", "password")
        assert non_existent is None
    
    def test_login_admin(self, db_session, test_admin):
        """Test admin login service"""
        login_data = AdminLogin(username=test_admin.username, password="testpass123")
        token = login_admin(db_session, login_data)
        
        assert token is not None
        assert isinstance(token, str)
        
        # Test wrong credentials
        wrong_login = AdminLogin(username=test_admin.username, password="wrongpass")
        wrong_token = login_admin(db_session, wrong_login)
        assert wrong_token is None


class TestQuestionService:
    """Test question service functions"""
    
    def test_create_page(self, db_session):
        """Test page creation service"""
        page_data = PageCreate(
            title="New Page",
            description="Test description",
            order_index=1
        )
        page = create_page(db_session, page_data)
        
        assert page.id is not None
        assert page.title == "New Page"
        assert page.description == "Test description"
        assert page.order_index == 1
    
    def test_get_pages(self, db_session, test_page):
        """Test getting all pages"""
        pages = get_pages(db_session)
        assert len(pages) >= 1
        assert test_page in pages
        
        # Test active only filter
        active_pages = get_pages(db_session, active_only=True)
        assert all(page.is_active for page in active_pages)
    
    def test_get_page_by_id(self, db_session, test_page):
        """Test getting page by ID"""
        page = get_page_by_id(db_session, test_page.id)
        assert page is not None
        assert page.id == test_page.id
        
        # Test non-existent page
        non_existent = get_page_by_id(db_session, 99999)
        assert non_existent is None
    
    def test_update_page(self, db_session, test_page):
        """Test page update service"""
        update_data = PageUpdate(
            title="Updated Title",
            description="Updated description",
            is_active=False
        )
        updated_page = update_page(db_session, test_page.id, update_data)
        
        assert updated_page is not None
        assert updated_page.title == "Updated Title"
        assert updated_page.description == "Updated description"
        assert updated_page.is_active is False
    
    def test_delete_page(self, db_session, test_page):
        """Test page deletion service"""
        page_id = test_page.id
        result = delete_page(db_session, page_id)
        
        assert result is True
        
        # Verify page is deleted
        deleted_page = get_page_by_id(db_session, page_id)
        assert deleted_page is None
    
    def test_create_question(self, db_session, test_page):
        """Test question creation service"""
        question_data = QuestionCreate(
            page_id=test_page.id,
            question_text="New question?",
            question_type=QuestionType.essay,
            order_index=1,
            is_required=True,
            essay_char_limit=300
        )
        question = create_question(db_session, question_data)
        
        assert question.id is not None
        assert question.question_text == "New question?"
        assert question.question_type == QuestionType.essay
    
    def test_get_questions_by_page(self, db_session, test_page, test_essay_question):
        """Test getting questions by page"""
        questions = get_questions_by_page(db_session, test_page.id)
        assert len(questions) >= 1
        assert test_essay_question in questions


class TestResponseService:
    """Test response service functions"""
    
    def test_create_student_response(self, db_session, sample_student_data):
        """Test student response creation"""
        response_data = StudentResponseCreate(
            session_id="new-session-123",
            **sample_student_data
        )
        response = create_student_response(db_session, response_data)
        
        assert response.id is not None
        assert response.session_id == "new-session-123"
        assert response.email == sample_student_data["email"]
    
    def test_get_student_response_by_session(self, db_session, test_student_response):
        """Test getting response by session ID"""
        response = get_student_response_by_session(db_session, test_student_response.session_id)
        assert response is not None
        assert response.id == test_student_response.id
        
        # Test non-existent session
        non_existent = get_student_response_by_session(db_session, "nonexistent-session")
        assert non_existent is None
    
    def test_complete_student_response(self, db_session, test_student_response):
        """Test completing student response"""
        # Initially not completed
        assert test_student_response.completed_at is None
        
        completed = complete_student_response(db_session, test_student_response.session_id)
        assert completed is not None
        assert completed.completed_at is not None
    
    def test_create_question_answer(self, db_session, test_student_response, test_essay_question):
        """Test question answer creation"""
        answer_data = QuestionAnswerCreate(
            response_id=test_student_response.id,
            question_id=test_essay_question.id,
            answer_text="My test answer",
            answer_value=None
        )
        answer = create_question_answer(db_session, answer_data)
        
        assert answer.id is not None
        assert answer.answer_text == "My test answer"
        
        # Test updating existing answer
        updated_data = QuestionAnswerCreate(
            response_id=test_student_response.id,
            question_id=test_essay_question.id,
            answer_text="Updated answer",
            answer_value=None
        )
        updated_answer = create_question_answer(db_session, updated_data)
        
        # Should be same answer ID but updated text
        assert updated_answer.id == answer.id
        assert updated_answer.answer_text == "Updated answer"
    
    def test_get_all_responses(self, db_session, test_student_response):
        """Test getting all responses"""
        responses = get_all_responses(db_session)
        assert len(responses) >= 1
        assert test_student_response in responses
    
    def test_get_response_statistics(self, db_session, test_student_response):
        """Test response statistics"""
        stats = get_response_statistics(db_session)
        
        assert "total_responses" in stats
        assert "completed_responses" in stats
        assert "incomplete_responses" in stats
        assert stats["total_responses"] >= 1
        assert stats["completed_responses"] + stats["incomplete_responses"] == stats["total_responses"]