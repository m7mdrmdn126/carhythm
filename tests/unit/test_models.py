import pytest
from app.models import Admin, Page, Question, StudentResponse, QuestionAnswer, QuestionType
from app.utils.security import get_password_hash
from sqlalchemy.exc import IntegrityError


class TestAdminModel:
    """Test Admin model"""
    
    def test_create_admin(self, db_session):
        """Test admin creation"""
        admin = Admin(
            username="testadmin",
            password_hash=get_password_hash("password123")
        )
        db_session.add(admin)
        db_session.commit()
        
        assert admin.id is not None
        assert admin.username == "testadmin"
        assert admin.created_at is not None
    
    def test_unique_username(self, db_session):
        """Test username uniqueness constraint"""
        admin1 = Admin(username="duplicate", password_hash="hash1")
        admin2 = Admin(username="duplicate", password_hash="hash2")
        
        db_session.add(admin1)
        db_session.commit()
        
        db_session.add(admin2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestPageModel:
    """Test Page model"""
    
    def test_create_page(self, db_session):
        """Test page creation"""
        page = Page(
            title="Test Page",
            description="Test description",
            order_index=1,
            is_active=True
        )
        db_session.add(page)
        db_session.commit()
        
        assert page.id is not None
        assert page.title == "Test Page"
        assert page.description == "Test description"
        assert page.order_index == 1
        assert page.is_active is True
        assert page.created_at is not None
    
    def test_page_defaults(self, db_session):
        """Test page default values"""
        page = Page(title="Simple Page")
        db_session.add(page)
        db_session.commit()
        
        assert page.order_index == 0
        assert page.is_active is True
        assert page.description is None


class TestQuestionModel:
    """Test Question model"""
    
    def test_create_essay_question(self, db_session, test_page):
        """Test essay question creation"""
        question = Question(
            page_id=test_page.id,
            question_text="What is your goal?",
            question_type=QuestionType.essay,
            order_index=1,
            is_required=True,
            essay_char_limit=300
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.id is not None
        assert question.page_id == test_page.id
        assert question.question_type == QuestionType.essay
        assert question.essay_char_limit == 300
        assert question.slider_min_label is None
    
    def test_create_slider_question(self, db_session, test_page):
        """Test slider question creation"""
        question = Question(
            page_id=test_page.id,
            question_text="Rate your interest",
            question_type=QuestionType.slider,
            order_index=1,
            is_required=True,
            slider_min_label="Low",
            slider_max_label="High"
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.id is not None
        assert question.question_type == QuestionType.slider
        assert question.slider_min_label == "Low"
        assert question.slider_max_label == "High"
        assert question.essay_char_limit is None
    
    def test_question_page_relationship(self, db_session, test_page):
        """Test question-page relationship"""
        question = Question(
            page_id=test_page.id,
            question_text="Test question",
            question_type=QuestionType.essay
        )
        db_session.add(question)
        db_session.commit()
        
        # Test relationship
        assert question.page == test_page
        assert question in test_page.questions


class TestStudentResponseModel:
    """Test StudentResponse model"""
    
    def test_create_student_response(self, db_session):
        """Test student response creation"""
        response = StudentResponse(
            session_id="test-session-123",
            email="test@example.com",
            full_name="John Doe",
            age_group="23-25",
            country="USA",
            origin_country="India"
        )
        db_session.add(response)
        db_session.commit()
        
        assert response.id is not None
        assert response.session_id == "test-session-123"
        assert response.email == "test@example.com"
        assert response.completed_at is None
        assert response.created_at is not None
    
    def test_unique_session_id(self, db_session):
        """Test session ID uniqueness"""
        response1 = StudentResponse(
            session_id="duplicate-session",
            email="test1@example.com",
            full_name="John1",
            age_group="23-25",
            country="USA",
            origin_country="USA"
        )
        response2 = StudentResponse(
            session_id="duplicate-session",
            email="test2@example.com",
            full_name="John2",
            age_group="23-25",
            country="USA",
            origin_country="USA"
        )
        
        db_session.add(response1)
        db_session.commit()
        
        db_session.add(response2)
        with pytest.raises(IntegrityError):
            db_session.commit()


class TestQuestionAnswerModel:
    """Test QuestionAnswer model"""
    
    def test_create_essay_answer(self, db_session, test_student_response, test_essay_question):
        """Test essay answer creation"""
        answer = QuestionAnswer(
            response_id=test_student_response.id,
            question_id=test_essay_question.id,
            answer_text="My career goal is to become a software engineer.",
            answer_value=None
        )
        db_session.add(answer)
        db_session.commit()
        
        assert answer.id is not None
        assert answer.response_id == test_student_response.id
        assert answer.question_id == test_essay_question.id
        assert answer.answer_text == "My career goal is to become a software engineer."
        assert answer.answer_value is None
    
    def test_create_slider_answer(self, db_session, test_student_response, test_slider_question):
        """Test slider answer creation"""
        answer = QuestionAnswer(
            response_id=test_student_response.id,
            question_id=test_slider_question.id,
            answer_text=None,
            answer_value=75.0
        )
        db_session.add(answer)
        db_session.commit()
        
        assert answer.id is not None
        assert answer.answer_text is None
        assert answer.answer_value == 75.0
    
    def test_answer_relationships(self, db_session, test_student_response, test_essay_question):
        """Test answer relationships"""
        answer = QuestionAnswer(
            response_id=test_student_response.id,
            question_id=test_essay_question.id,
            answer_text="Test answer"
        )
        db_session.add(answer)
        db_session.commit()
        
        # Test relationships
        assert answer.response == test_student_response
        assert answer.question == test_essay_question
        assert answer in test_student_response.answers
        assert answer in test_essay_question.answers