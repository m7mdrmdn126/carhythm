"""
Comprehensive unit tests for all service modules
"""
import pytest
import json
from datetime import datetime
from app.services import auth, question_service, response_service
from app.services.question_pool_service import QuestionPoolService
from app.services.csv_import_service import CSVImportExportService
from app.schemas import (
    AdminCreate, AdminLogin, PageCreate, PageUpdate, QuestionCreate, QuestionUpdate,
    StudentResponseCreate, QuestionAnswerCreate
)
from app.schemas.question_pool import (
    CategoryCreate, CategoryUpdate, QuestionPoolCreate, QuestionPoolUpdate,
    QuestionPageAssignmentCreate, QuestionPoolFilter
)
from app.models import Admin, Page, Question, QuestionType, StudentResponse, QuestionAnswer, Category, QuestionPool
from app.utils.security import verify_password, verify_token


class TestAuthService:
    """Test authentication service"""
    
    def test_create_admin(self, db_session):
        """Test admin creation"""
        admin_data = AdminCreate(username="newadmin", password="securepass123")
        admin = auth.create_admin(db_session, admin_data)
        
        assert admin.id is not None
        assert admin.username == "newadmin"
        assert verify_password("securepass123", admin.password_hash)
    
    def test_authenticate_admin_success(self, db_session, test_admin):
        """Test successful admin authentication"""
        authenticated = auth.authenticate_admin(db_session, "testadmin", "testpass123")
        
        assert authenticated is not None
        assert authenticated.username == "testadmin"
    
    def test_authenticate_admin_wrong_password(self, db_session, test_admin):
        """Test authentication with wrong password"""
        authenticated = auth.authenticate_admin(db_session, "testadmin", "wrongpassword")
        
        assert authenticated is None
    
    def test_authenticate_admin_nonexistent_user(self, db_session):
        """Test authentication with nonexistent user"""
        authenticated = auth.authenticate_admin(db_session, "nonexistent", "password")
        
        assert authenticated is None
    
    def test_get_admin_by_username(self, db_session, test_admin):
        """Test get admin by username"""
        admin = auth.get_admin_by_username(db_session, "testadmin")
        
        assert admin is not None
        assert admin.username == "testadmin"
    
    def test_login_admin_success(self, db_session, test_admin):
        """Test successful admin login"""
        login_data = AdminLogin(username="testadmin", password="testpass123")
        token = auth.login_admin(db_session, login_data)
        
        assert token is not None
        # Verify token contains username
        username = verify_token(token)
        assert username == "testadmin"
    
    def test_login_admin_failure(self, db_session, test_admin):
        """Test failed admin login"""
        login_data = AdminLogin(username="testadmin", password="wrongpassword")
        token = auth.login_admin(db_session, login_data)
        
        assert token is None


class TestQuestionService:
    """Test question service"""
    
    def test_create_page(self, db_session):
        """Test page creation"""
        page_data = PageCreate(
            title="Test Page",
            description="Test description",
            order_index=1
        )
        page = question_service.create_page(db_session, page_data)
        
        assert page.id is not None
        assert page.title == "Test Page"
        assert page.is_active is True
    
    def test_get_pages(self, db_session, multiple_pages):
        """Test getting all pages"""
        pages = question_service.get_pages(db_session)
        
        assert len(pages) >= 3
        assert all(isinstance(p, Page) for p in pages)
    
    def test_get_pages_active_only(self, db_session):
        """Test getting only active pages"""
        # Create inactive page
        inactive_page = Page(title="Inactive", order_index=10, is_active=False)
        db_session.add(inactive_page)
        
        # Create active page
        active_page = Page(title="Active", order_index=11, is_active=True)
        db_session.add(active_page)
        db_session.commit()
        
        pages = question_service.get_pages(db_session, active_only=True)
        
        assert all(p.is_active for p in pages)
        assert any(p.title == "Active" for p in pages)
        assert not any(p.title == "Inactive" for p in pages)
    
    def test_get_page_by_id(self, db_session, test_page):
        """Test getting page by ID"""
        page = question_service.get_page_by_id(db_session, test_page.id)
        
        assert page is not None
        assert page.id == test_page.id
        assert page.title == test_page.title
    
    def test_update_page(self, db_session, test_page):
        """Test updating a page"""
        update_data = PageUpdate(
            title="Updated Title",
            description="Updated description",
            is_active=False
        )
        updated_page = question_service.update_page(db_session, test_page.id, update_data)
        
        assert updated_page.title == "Updated Title"
        assert updated_page.description == "Updated description"
        assert updated_page.is_active is False
    
    def test_delete_page(self, db_session, test_page):
        """Test deleting a page"""
        page_id = test_page.id
        result = question_service.delete_page(db_session, page_id)
        
        assert result is True
        
        # Verify page is deleted
        deleted_page = db_session.query(Page).filter(Page.id == page_id).first()
        assert deleted_page is None
    
    def test_create_essay_question(self, db_session, test_page):
        """Test creating essay question"""
        question_data = QuestionCreate(
            page_id=test_page.id,
            question_text="What are your goals?",
            question_type=QuestionType.essay,
            order_index=1,
            is_required=True,
            essay_char_limit=500
        )
        question = question_service.create_question(db_session, question_data)
        
        assert question.id is not None
        assert question.question_type == QuestionType.essay
        assert question.essay_char_limit == 500
    
    def test_create_mcq_question(self, db_session, test_page):
        """Test creating MCQ question"""
        question_data = QuestionCreate(
            page_id=test_page.id,
            question_text="Choose your preference",
            question_type=QuestionType.mcq,
            order_index=1,
            is_required=True,
            mcq_options=["Option A", "Option B", "Option C"],
            mcq_correct_answer=[0],
            allow_multiple_selection=False
        )
        question = question_service.create_question(db_session, question_data)
        
        assert question.id is not None
        assert question.mcq_options is not None
        options = json.loads(question.mcq_options)
        assert len(options) == 3
    
    def test_create_ordering_question(self, db_session, test_page):
        """Test creating ordering question"""
        question_data = QuestionCreate(
            page_id=test_page.id,
            question_text="Rank these items",
            question_type=QuestionType.ordering,
            order_index=1,
            is_required=True,
            ordering_options=["Item 1", "Item 2", "Item 3"],
            randomize_order=True
        )
        question = question_service.create_question(db_session, question_data)
        
        assert question.id is not None
        assert question.ordering_options is not None
        options = json.loads(question.ordering_options)
        assert len(options) == 3
    
    def test_get_questions_by_page(self, db_session, test_page, test_essay_question):
        """Test getting questions by page"""
        questions = question_service.get_questions_by_page(db_session, test_page.id)
        
        assert len(questions) >= 1
        assert test_essay_question.id in [q.id for q in questions]
    
    def test_get_question_by_id(self, db_session, test_essay_question):
        """Test getting question by ID"""
        question = question_service.get_question_by_id(db_session, test_essay_question.id)
        
        assert question is not None
        assert question.id == test_essay_question.id
    
    def test_update_question(self, db_session, test_essay_question):
        """Test updating question"""
        update_data = QuestionUpdate(
            question_text="Updated question text",
            is_required=False
        )
        updated_question = question_service.update_question(
            db_session, test_essay_question.id, update_data
        )
        
        assert updated_question.question_text == "Updated question text"
        assert updated_question.is_required is False
    
    def test_delete_question(self, db_session, test_essay_question):
        """Test deleting question"""
        question_id = test_essay_question.id
        result = question_service.delete_question(db_session, question_id)
        
        assert result is True
        
        # Verify deletion
        deleted = db_session.query(Question).filter(Question.id == question_id).first()
        assert deleted is None
    
    def test_update_question_image(self, db_session, test_essay_question):
        """Test updating question image"""
        image_path = "/uploads/test_image.jpg"
        updated_question = question_service.update_question_image(
            db_session, test_essay_question.id, image_path
        )
        
        assert updated_question.image_path == image_path


class TestResponseService:
    """Test response service"""
    
    def test_create_student_response(self, db_session):
        """Test creating student response"""
        response_data = StudentResponseCreate(
            session_id="test-session-123",
            email="test@example.com",
            full_name="John Doe",
            age_group="23-25",
            country="USA",
            origin_country="India"
        )
        response = response_service.create_student_response(db_session, response_data)
        
        assert response.id is not None
        assert response.session_id == "test-session-123"
        assert response.email == "test@example.com"
    
    def test_get_student_response_by_session(self, db_session, test_student_response):
        """Test getting response by session ID"""
        response = response_service.get_student_response_by_session(
            db_session, test_student_response.session_id
        )
        
        assert response is not None
        assert response.id == test_student_response.id
    
    def test_complete_student_response(self, db_session, test_student_response):
        """Test completing student response"""
        completed = response_service.complete_student_response(
            db_session, test_student_response.session_id
        )
        
        assert completed is not None
        assert completed.completed_at is not None
    
    def test_create_question_answer(self, db_session, test_student_response, test_essay_question):
        """Test creating question answer"""
        answer_data = QuestionAnswerCreate(
            response_id=test_student_response.id,
            question_id=test_essay_question.id,
            answer_text="My answer text",
            answer_value=None,
            answer_json=None
        )
        answer = response_service.create_question_answer(db_session, answer_data)
        
        assert answer.id is not None
        assert answer.answer_text == "My answer text"
    
    def test_update_existing_answer(self, db_session, test_student_response, test_essay_question):
        """Test updating an existing answer"""
        # Create initial answer
        answer_data1 = QuestionAnswerCreate(
            response_id=test_student_response.id,
            question_id=test_essay_question.id,
            answer_text="Initial answer",
            answer_value=None,
            answer_json=None
        )
        answer1 = response_service.create_question_answer(db_session, answer_data1)
        answer1_id = answer1.id
        
        # Update answer
        answer_data2 = QuestionAnswerCreate(
            response_id=test_student_response.id,
            question_id=test_essay_question.id,
            answer_text="Updated answer",
            answer_value=None,
            answer_json=None
        )
        answer2 = response_service.create_question_answer(db_session, answer_data2)
        
        # Should have same ID (updated, not created new)
        assert answer2.id == answer1_id
        assert answer2.answer_text == "Updated answer"
    
    def test_get_all_responses(self, db_session, test_student_response):
        """Test getting all responses"""
        responses = response_service.get_all_responses(db_session)
        
        assert len(responses) >= 1
        assert test_student_response.id in [r.id for r in responses]
    
    def test_get_response_with_answers(self, db_session, test_student_response):
        """Test getting response with answers"""
        response = response_service.get_response_with_answers(db_session, test_student_response.id)
        
        assert response is not None
        assert response.id == test_student_response.id
    
    def test_get_answers_by_response(self, db_session, test_question_answers):
        """Test getting answers by response"""
        response_id = test_question_answers[0].response_id
        answers = response_service.get_answers_by_response(db_session, response_id)
        
        assert len(answers) >= 2
        assert all(a.response_id == response_id for a in answers)
    
    def test_delete_student_response(self, db_session, test_student_response):
        """Test deleting student response"""
        response_id = test_student_response.id
        result = response_service.delete_student_response(db_session, response_id)
        
        assert result is True
        
        # Verify deletion
        deleted = db_session.query(StudentResponse).filter(StudentResponse.id == response_id).first()
        assert deleted is None
    
    def test_get_response_statistics(self, db_session):
        """Test getting response statistics"""
        # Create completed and incomplete responses
        response1 = StudentResponse(
            session_id="session-1",
            email="test1@test.com",
            full_name="Test 1",
            age_group="23-25",
            country="USA",
            origin_country="USA",
            completed_at=datetime.utcnow()
        )
        response2 = StudentResponse(
            session_id="session-2",
            email="test2@test.com",
            full_name="Test 2",
            age_group="23-25",
            country="USA",
            origin_country="USA"
        )
        db_session.add(response1)
        db_session.add(response2)
        db_session.commit()
        
        stats = response_service.get_response_statistics(db_session)
        
        assert stats["total_responses"] >= 2
        assert stats["completed_responses"] >= 1
        assert stats["incomplete_responses"] >= 1


class TestQuestionPoolService:
    """Test question pool service"""
    
    def test_create_category(self, db_session):
        """Test creating category"""
        category_data = CategoryCreate(
            name="Test Category",
            description="Test description",
            color="#ff0000"
        )
        category = QuestionPoolService.create_category(db_session, category_data)
        
        assert category.id is not None
        assert category.name == "Test Category"
        assert category.color == "#ff0000"
    
    def test_get_categories(self, db_session, multiple_categories):
        """Test getting categories"""
        categories = QuestionPoolService.get_categories(db_session)
        
        assert len(categories) >= 3
        assert all(c.is_active for c in categories)
    
    def test_update_category(self, db_session, test_category):
        """Test updating category"""
        update_data = CategoryUpdate(
            name="Updated Category",
            color="#00ff00",
            is_active=False
        )
        updated = QuestionPoolService.update_category(db_session, test_category.id, update_data)
        
        assert updated.name == "Updated Category"
        assert updated.color == "#00ff00"
        assert updated.is_active is False
    
    def test_delete_category(self, db_session, test_category):
        """Test deleting category"""
        category_id = test_category.id
        result = QuestionPoolService.delete_category(db_session, category_id)
        
        assert result is True
        
        deleted = db_session.query(Category).filter(Category.id == category_id).first()
        assert deleted is None
    
    def test_create_question_pool(self, db_session, test_category):
        """Test creating question in pool"""
        question_data = QuestionPoolCreate(
            title="Pool Question",
            question_text="What is your goal?",
            question_type="essay",
            category_id=test_category.id,
            is_required=True,
            essay_char_limit=500,
            created_by="admin"
        )
        question = QuestionPoolService.create_question_pool(db_session, question_data)
        
        assert question.id is not None
        assert question.title == "Pool Question"
        assert question.usage_count == 0
    
    def test_get_questions_pool_with_filters(self, db_session, test_question_pool, test_category):
        """Test getting questions with filters"""
        filters = QuestionPoolFilter(
            category_id=test_category.id,
            question_type="essay",
            skip=0,
            limit=10
        )
        questions = QuestionPoolService.get_questions_pool(db_session, filters)
        
        assert len(questions) >= 1
        assert all(q.category_id == test_category.id for q in questions)
        assert all(q.question_type == "essay" for q in questions)
    
    def test_search_questions_pool(self, db_session, test_question_pool):
        """Test searching questions in pool"""
        filters = QuestionPoolFilter(
            search_text="environment",
            skip=0,
            limit=10
        )
        questions = QuestionPoolService.get_questions_pool(db_session, filters)
        
        # Should find questions with "environment" in title or text
        assert any("environment" in q.title.lower() or "environment" in q.question_text.lower() for q in questions)
    
    def test_update_question_pool(self, db_session, test_question_pool):
        """Test updating question in pool"""
        update_data = QuestionPoolUpdate(
            title="Updated Pool Question",
            question_text="Updated question text"
        )
        updated = QuestionPoolService.update_question_pool(
            db_session, test_question_pool.id, update_data
        )
        
        assert updated.title == "Updated Pool Question"
        assert updated.question_text == "Updated question text"
    
    def test_delete_question_pool(self, db_session, test_question_pool):
        """Test deleting question from pool"""
        question_id = test_question_pool.id
        result = QuestionPoolService.delete_question_pool(db_session, question_id)
        
        assert result is True
        
        deleted = db_session.query(QuestionPool).filter(QuestionPool.id == question_id).first()
        assert deleted is None
    
    def test_assign_question_to_page(self, db_session, test_question_pool, test_page):
        """Test assigning question to page"""
        assignment_data = QuestionPageAssignmentCreate(
            question_pool_id=test_question_pool.id,
            page_id=test_page.id,
            order_index=0,
            assigned_by="admin"
        )
        assignment = QuestionPoolService.assign_question_to_page(db_session, assignment_data)
        
        assert assignment.id is not None
        assert assignment.question_pool_id == test_question_pool.id
        assert assignment.page_id == test_page.id
    
    def test_get_pool_statistics(self, db_session, test_question_pool):
        """Test getting pool statistics"""
        stats = QuestionPoolService.get_pool_statistics(db_session)
        
        assert "total_questions" in stats
        assert "by_type" in stats
        assert "by_category" in stats
        assert stats["total_questions"] >= 1


class TestCSVImportService:
    """Test CSV import/export service"""
    
    def test_validate_and_import_essay_csv(self, db_session, test_category):
        """Test importing essay questions from CSV"""
        csv_content = """title,question_text,category_name,is_required,essay_char_limit
Essay Q1,What is your goal?,Career Exploration,TRUE,500
Essay Q2,Describe your background,Career Exploration,TRUE,400"""
        
        result = CSVImportExportService.validate_and_import_csv(
            db_session, csv_content, "essay", "test.csv", "admin"
        )
        
        assert result.total_rows == 2
        assert result.successful_imports == 2
        assert result.failed_imports == 0
    
    def test_validate_and_import_slider_csv(self, db_session, test_category):
        """Test importing slider questions from CSV"""
        csv_content = """title,question_text,category_name,is_required,slider_min_label,slider_max_label
Slider Q1,Rate your interest,Career Exploration,TRUE,Low,High
Slider Q2,Rate your skill,Career Exploration,TRUE,Beginner,Expert"""
        
        result = CSVImportExportService.validate_and_import_csv(
            db_session, csv_content, "slider", "test.csv", "admin"
        )
        
        assert result.total_rows == 2
        assert result.successful_imports == 2
    
    def test_import_csv_with_errors(self, db_session, test_category):
        """Test CSV import with invalid data"""
        csv_content = """title,question_text,category_name,is_required,essay_char_limit
,Missing title,Career Exploration,TRUE,500
Valid Title,Valid question,Career Exploration,TRUE,400
Invalid Limit,Some text,Career Exploration,TRUE,invalid"""
        
        result = CSVImportExportService.validate_and_import_csv(
            db_session, csv_content, "essay", "test.csv", "admin"
        )
        
        assert result.total_rows == 3
        assert result.failed_imports >= 1
        assert len(result.errors) >= 1
    
    def test_process_essay_row(self, db_session, test_category):
        """Test processing essay row"""
        row = {
            "title": "Test Essay",
            "question_text": "What is your goal?",
            "category_name": test_category.name,
            "is_required": "TRUE",
            "essay_char_limit": "500"
        }
        
        categories = {test_category.name: test_category.id}
        result = CSVImportExportService._process_essay_row(row, categories)
        
        assert result["title"] == "Test Essay"
        assert result["question_type"] == "essay"
        assert result["essay_char_limit"] == 500
    
    def test_process_mcq_row(self, db_session, test_category):
        """Test processing MCQ row"""
        row = {
            "title": "Test MCQ",
            "question_text": "Choose option",
            "category_name": test_category.name,
            "is_required": "TRUE",
            "option_1": "Option A",
            "option_2": "Option B",
            "option_3": "Option C",
            "correct_answers": "1,2",
            "allow_multiple_selection": "TRUE"
        }
        
        categories = {test_category.name: test_category.id}
        result = CSVImportExportService._process_mcq_row(row, categories)
        
        assert result["title"] == "Test MCQ"
        assert result["question_type"] == "mcq"
        assert len(result["mcq_options"]) == 3
        assert result["allow_multiple_selection"] is True
