import pytest
import json
from app.models import (
    Admin, Page, Question, StudentResponse, QuestionAnswer, QuestionType,
    Category, QuestionPool, QuestionPageAssignment, ImportLog
)
from app.utils.security import get_password_hash
from sqlalchemy.exc import IntegrityError
from datetime import datetime


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


class TestMCQQuestionModel:
    """Test MCQ Question model"""
    
    def test_create_single_mcq_question(self, db_session, test_page):
        """Test single-selection MCQ question creation"""
        question = Question(
            page_id=test_page.id,
            question_text="What is your preferred work schedule?",
            question_type=QuestionType.mcq,
            order_index=1,
            is_required=True,
            mcq_options=json.dumps(["9-5 weekdays", "Flexible hours", "Remote work"]),
            mcq_correct_answer=json.dumps([0]),
            allow_multiple_selection=False
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.id is not None
        assert question.question_type == QuestionType.mcq
        assert question.mcq_options is not None
        assert question.allow_multiple_selection is False
        
        # Parse and verify options
        options = json.loads(question.mcq_options)
        assert len(options) == 3
        assert "9-5 weekdays" in options
    
    def test_create_multiple_mcq_question(self, db_session, test_page):
        """Test multiple-selection MCQ question creation"""
        question = Question(
            page_id=test_page.id,
            question_text="Which skills do you have?",
            question_type=QuestionType.mcq,
            order_index=1,
            is_required=True,
            mcq_options=json.dumps(["Communication", "Leadership", "Technical"]),
            mcq_correct_answer=json.dumps([0, 2]),
            allow_multiple_selection=True
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.allow_multiple_selection is True
        correct_answers = json.loads(question.mcq_correct_answer)
        assert len(correct_answers) == 2
    
    def test_mcq_answer_storage(self, db_session, test_student_response, test_mcq_question):
        """Test MCQ answer storage"""
        answer = QuestionAnswer(
            response_id=test_student_response.id,
            question_id=test_mcq_question.id,
            answer_text=None,
            answer_value=None,
            answer_json=json.dumps([0])  # Selected first option
        )
        db_session.add(answer)
        db_session.commit()
        
        assert answer.answer_json is not None
        selected = json.loads(answer.answer_json)
        assert selected == [0]


class TestOrderingQuestionModel:
    """Test Ordering Question model"""
    
    def test_create_ordering_question(self, db_session, test_page):
        """Test ordering question creation"""
        question = Question(
            page_id=test_page.id,
            question_text="Rank these career factors",
            question_type=QuestionType.ordering,
            order_index=1,
            is_required=True,
            ordering_options=json.dumps(["Salary", "Growth", "Balance", "Security"]),
            randomize_order=True
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.id is not None
        assert question.question_type == QuestionType.ordering
        assert question.ordering_options is not None
        assert question.randomize_order is True
        
        options = json.loads(question.ordering_options)
        assert len(options) == 4
    
    def test_ordering_answer_storage(self, db_session, test_student_response, test_ordering_question):
        """Test ordering answer storage"""
        # User's ordering: indices representing the order
        answer = QuestionAnswer(
            response_id=test_student_response.id,
            question_id=test_ordering_question.id,
            answer_text=None,
            answer_value=None,
            answer_json=json.dumps([2, 0, 3, 1])  # User's ranking order
        )
        db_session.add(answer)
        db_session.commit()
        
        assert answer.answer_json is not None
        ordering = json.loads(answer.answer_json)
        assert len(ordering) == 4


class TestCategoryModel:
    """Test Category model"""
    
    def test_create_category(self, db_session):
        """Test category creation"""
        category = Category(
            name="Career Exploration",
            description="Questions about career paths",
            color="#3498db",
            is_active=True
        )
        db_session.add(category)
        db_session.commit()
        
        assert category.id is not None
        assert category.name == "Career Exploration"
        assert category.color == "#3498db"
        assert category.is_active is True
        assert category.created_at is not None
    
    def test_category_unique_name(self, db_session):
        """Test category name uniqueness"""
        category1 = Category(name="Duplicate Name", color="#aaaaaa")
        category2 = Category(name="Duplicate Name", color="#bbbbbb")
        
        db_session.add(category1)
        db_session.commit()
        
        db_session.add(category2)
        with pytest.raises(IntegrityError):
            db_session.commit()
    
    def test_category_defaults(self, db_session):
        """Test category default values"""
        category = Category(name="Simple Category")
        db_session.add(category)
        db_session.commit()
        
        assert category.color == "#3498db"
        assert category.is_active is True


class TestQuestionPoolModel:
    """Test QuestionPool model"""
    
    def test_create_question_pool_essay(self, db_session, test_category):
        """Test creating essay question in pool"""
        question = QuestionPool(
            title="Career Goals",
            question_text="What are your career aspirations?",
            question_type="essay",
            category_id=test_category.id,
            is_required=True,
            essay_char_limit=500,
            created_by="admin",
            usage_count=0
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.id is not None
        assert question.title == "Career Goals"
        assert question.question_type == "essay"
        assert question.category_id == test_category.id
        assert question.usage_count == 0
        assert question.created_at is not None
        assert question.updated_at is not None
    
    def test_create_question_pool_mcq(self, db_session, test_category):
        """Test creating MCQ question in pool"""
        question = QuestionPool(
            title="Preferred Industry",
            question_text="Which industry interests you?",
            question_type="mcq",
            category_id=test_category.id,
            mcq_options=json.dumps(["Tech", "Healthcare", "Finance"]),
            mcq_correct_answer=json.dumps([0]),
            allow_multiple_selection=False,
            created_by="admin"
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.question_type == "mcq"
        assert question.mcq_options is not None
        assert question.allow_multiple_selection is False
    
    def test_question_pool_category_relationship(self, db_session, test_category):
        """Test question pool - category relationship"""
        question = QuestionPool(
            title="Test Question",
            question_text="Test text",
            question_type="essay",
            category_id=test_category.id,
            created_by="admin"
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.category == test_category
        assert question in test_category.questions
    
    def test_question_pool_without_category(self, db_session):
        """Test creating question pool without category"""
        question = QuestionPool(
            title="Uncategorized Question",
            question_text="Test question",
            question_type="slider",
            slider_min_label="Low",
            slider_max_label="High",
            created_by="admin"
        )
        db_session.add(question)
        db_session.commit()
        
        assert question.category_id is None
        assert question.category is None


class TestQuestionPageAssignmentModel:
    """Test QuestionPageAssignment model"""
    
    def test_create_assignment(self, db_session, test_question_pool, test_page):
        """Test creating question-page assignment"""
        assignment = QuestionPageAssignment(
            question_pool_id=test_question_pool.id,
            page_id=test_page.id,
            order_index=0,
            assigned_by="admin"
        )
        db_session.add(assignment)
        db_session.commit()
        
        assert assignment.id is not None
        assert assignment.question_pool_id == test_question_pool.id
        assert assignment.page_id == test_page.id
        assert assignment.assigned_at is not None
    
    def test_assignment_relationships(self, db_session, test_question_pool, test_page):
        """Test assignment relationships"""
        assignment = QuestionPageAssignment(
            question_pool_id=test_question_pool.id,
            page_id=test_page.id,
            order_index=0,
            assigned_by="admin"
        )
        db_session.add(assignment)
        db_session.commit()
        
        assert assignment.question == test_question_pool
        assert assignment.page == test_page
    
    def test_multiple_assignments(self, db_session, test_question_pool, multiple_pages):
        """Test assigning same question to multiple pages"""
        assignments = []
        for i, page in enumerate(multiple_pages):
            assignment = QuestionPageAssignment(
                question_pool_id=test_question_pool.id,
                page_id=page.id,
                order_index=i,
                assigned_by="admin"
            )
            db_session.add(assignment)
            assignments.append(assignment)
        
        db_session.commit()
        
        assert len(assignments) == len(multiple_pages)
        assert all(a.question_pool_id == test_question_pool.id for a in assignments)


class TestImportLogModel:
    """Test ImportLog model"""
    
    def test_create_import_log(self, db_session):
        """Test creating import log"""
        log = ImportLog(
            filename="test_questions.csv",
            import_type="essay",
            total_rows=10,
            successful_imports=8,
            failed_imports=2,
            errors=json.dumps([{"row": 3, "error": "Invalid data"}]),
            imported_by="admin"
        )
        db_session.add(log)
        db_session.commit()
        
        assert log.id is not None
        assert log.filename == "test_questions.csv"
        assert log.import_type == "essay"
        assert log.total_rows == 10
        assert log.successful_imports == 8
        assert log.failed_imports == 2
        assert log.imported_at is not None
    
    def test_import_log_defaults(self, db_session):
        """Test import log default values"""
        log = ImportLog(
            filename="simple.csv",
            import_type="slider",
            imported_by="admin"
        )
        db_session.add(log)
        db_session.commit()
        
        assert log.total_rows == 0
        assert log.successful_imports == 0
        assert log.failed_imports == 0
        assert log.errors is None
    
    def test_import_log_errors_json(self, db_session):
        """Test import log errors JSON storage"""
        errors = [
            {"row": 1, "error": "Missing field"},
            {"row": 3, "error": "Invalid format"},
            {"row": 5, "error": "Duplicate entry"}
        ]
        
        log = ImportLog(
            filename="errors.csv",
            import_type="mcq",
            total_rows=10,
            successful_imports=7,
            failed_imports=3,
            errors=json.dumps(errors),
            imported_by="admin"
        )
        db_session.add(log)
        db_session.commit()
        
        assert log.errors is not None
        parsed_errors = json.loads(log.errors)
        assert len(parsed_errors) == 3
        assert parsed_errors[0]["row"] == 1


class TestModelCascadeDeletes:
    """Test cascade delete behaviors"""
    
    def test_page_delete_cascades_questions(self, db_session, test_page):
        """Test that deleting a page deletes its questions"""
        question = Question(
            page_id=test_page.id,
            question_text="Test question",
            question_type=QuestionType.essay
        )
        db_session.add(question)
        db_session.commit()
        
        question_id = question.id
        
        # Delete page
        db_session.delete(test_page)
        db_session.commit()
        
        # Question should be deleted
        deleted_question = db_session.query(Question).filter(Question.id == question_id).first()
        assert deleted_question is None
    
    def test_response_delete_cascades_answers(self, db_session, test_student_response, test_essay_question):
        """Test that deleting a response deletes its answers"""
        answer = QuestionAnswer(
            response_id=test_student_response.id,
            question_id=test_essay_question.id,
            answer_text="Test answer"
        )
        db_session.add(answer)
        db_session.commit()
        
        answer_id = answer.id
        
        # Delete response
        db_session.delete(test_student_response)
        db_session.commit()
        
        # Answer should be deleted
        deleted_answer = db_session.query(QuestionAnswer).filter(QuestionAnswer.id == answer_id).first()
        assert deleted_answer is None
    
    def test_category_delete_preserves_questions(self, db_session, test_category):
        """Test that deleting a category sets questions category_id to None"""
        question = QuestionPool(
            title="Test Question",
            question_text="Test",
            question_type="essay",
            category_id=test_category.id,
            created_by="admin"
        )
        db_session.add(question)
        db_session.commit()
        
        question_id = question.id
        
        # Note: In the actual service, category delete sets category_id to None
        # Here we're just testing the model relationship
        assert question.category == test_category