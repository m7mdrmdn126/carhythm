import pytest
import tempfile
import os
import json
import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import Base, get_db
from app.models import (
    Admin, Page, Question, StudentResponse, QuestionAnswer, QuestionType,
    Category, QuestionPool, QuestionPageAssignment, ImportLog
)
from app.utils.security import get_password_hash

# Test database setup
@pytest.fixture(scope="session")
def test_db():
    """Create a temporary test database"""
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    yield TestingSessionLocal
    
    # Close all connections before cleaning up
    engine.dispose()
    os.close(db_fd)
    try:
        os.unlink(db_path)
    except PermissionError:
        # On Windows, the file might still be locked
        pass

@pytest.fixture
def db_session(test_db):
    """Create a database session for testing"""
    session = test_db()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def client(test_db):
    """Create a test client with test database"""
    def override_get_db():
        session = test_db()
        try:
            yield session
        finally:
            session.close()
    
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()

@pytest.fixture
def test_admin(db_session):
    """Create a test admin user"""
    admin = Admin(
        username="testadmin",
        password_hash=get_password_hash("testpass123")
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def test_page(db_session):
    """Create a test page"""
    page = Page(
        title="Test Page",
        description="A test page for examination",
        order_index=1,
        is_active=True
    )
    db_session.add(page)
    db_session.commit()
    db_session.refresh(page)
    return page

@pytest.fixture
def test_essay_question(db_session, test_page):
    """Create a test essay question"""
    question = Question(
        page_id=test_page.id,
        question_text="What are your career goals?",
        question_type=QuestionType.essay,
        order_index=1,
        is_required=True,
        essay_char_limit=500
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def test_slider_question(db_session, test_page):
    """Create a test slider question"""
    question = Question(
        page_id=test_page.id,
        question_text="How much do you enjoy teamwork?",
        question_type=QuestionType.slider,
        order_index=2,
        is_required=True,
        slider_min_label="Not at all",
        slider_max_label="Very much"
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def test_student_response(db_session):
    """Create a test student response with unique session ID"""
    response = StudentResponse(
        session_id=f"test-session-{uuid.uuid4().hex[:12]}",  # Unique session ID for each test
        email="test@example.com",
        full_name="John Doe",
        age_group="23-25",
        country="United States",
        origin_country="United States"
    )
    db_session.add(response)
    db_session.commit()
    db_session.refresh(response)
    return response

@pytest.fixture
def authenticated_admin_client(client, test_admin):
    """Create a client with admin authentication"""
    # Login the admin to set up session cookies
    client.post("/admin/login", data={
        "username": test_admin.username,
        "password": "testpass123"
    }, follow_redirects=False)
    
    # The client now has the session cookie set automatically by TestClient
    return client

@pytest.fixture
def sample_questions_data():
    """Sample question data for testing"""
    return [
        {
            "question_text": "Describe your ideal work environment.",
            "question_type": "essay",
            "order_index": 1,
            "is_required": True,
            "essay_char_limit": 300
        },
        {
            "question_text": "Rate your interest in leadership roles.",
            "question_type": "slider",
            "order_index": 2,
            "is_required": True,
            "slider_min_label": "No interest",
            "slider_max_label": "Very interested"
        }
    ]

@pytest.fixture
def sample_student_data():
    """Sample student information for testing"""
    return {
        "email": "student@test.com",
        "full_name": "Jane Student",
        "age_group": "19-22",
        "country": "Canada",
        "origin_country": "India"
    }

@pytest.fixture
def test_mcq_question(db_session, test_page):
    """Create a test multiple choice question"""
    question = Question(
        page_id=test_page.id,
        question_text="What is your preferred work schedule?",
        question_type=QuestionType.mcq,
        order_index=3,
        is_required=True,
        mcq_options=json.dumps(["9-5 weekdays", "Flexible hours", "Remote work", "Shift work"]),
        mcq_correct_answer=json.dumps([0]),  # First option is "correct"
        allow_multiple_selection=False
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def test_mcq_multiple_question(db_session, test_page):
    """Create a test multiple choice question with multiple selections allowed"""
    question = Question(
        page_id=test_page.id,
        question_text="Which skills do you possess? (Select all that apply)",
        question_type=QuestionType.mcq,
        order_index=4,
        is_required=True,
        mcq_options=json.dumps(["Communication", "Leadership", "Technical", "Creative", "Analytical"]),
        mcq_correct_answer=json.dumps([0, 1]),
        allow_multiple_selection=True
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def test_ordering_question(db_session, test_page):
    """Create a test ordering question"""
    question = Question(
        page_id=test_page.id,
        question_text="Rank these career factors by importance to you",
        question_type=QuestionType.ordering,
        order_index=5,
        is_required=True,
        ordering_options=json.dumps(["Salary", "Work-life balance", "Career growth", "Job security"]),
        randomize_order=True
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def test_category(db_session):
    """Create a test category"""
    # First try to get existing category to avoid unique constraint errors
    existing = db_session.query(Category).filter(Category.name == "Career Exploration").first()
    if existing:
        return existing
    
    category = Category(
        name="Career Exploration",
        description="Questions about career paths and preferences",
        color="#3498db",
        is_active=True
    )
    db_session.add(category)
    db_session.commit()
    db_session.refresh(category)
    return category

@pytest.fixture
def test_question_pool(db_session, test_category):
    """Create a test question in the pool"""
    question = QuestionPool(
        title="Work Environment Preference",
        question_text="Describe your ideal work environment",
        question_type="essay",
        category_id=test_category.id,
        is_required=True,
        essay_char_limit=500,
        created_by="testadmin",
        usage_count=0
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def test_question_pool_slider(db_session, test_category):
    """Create a test slider question in the pool"""
    question = QuestionPool(
        title="Leadership Interest",
        question_text="How interested are you in leadership roles?",
        question_type="slider",
        category_id=test_category.id,
        is_required=True,
        slider_min_label="Not interested",
        slider_max_label="Very interested",
        created_by="testadmin",
        usage_count=0
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def test_question_pool_mcq(db_session, test_category):
    """Create a test MCQ question in the pool"""
    question = QuestionPool(
        title="Preferred Industry",
        question_text="Which industry are you most interested in?",
        question_type="mcq",
        category_id=test_category.id,
        is_required=True,
        mcq_options=json.dumps(["Technology", "Healthcare", "Finance", "Education"]),
        mcq_correct_answer=json.dumps([0]),
        allow_multiple_selection=False,
        created_by="testadmin",
        usage_count=0
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def test_question_pool_ordering(db_session, test_category):
    """Create a test ordering question in the pool"""
    question = QuestionPool(
        title="Priority Ranking",
        question_text="Rank these job factors by importance",
        question_type="ordering",
        category_id=test_category.id,
        is_required=True,
        ordering_options=json.dumps(["Compensation", "Growth", "Culture", "Location"]),
        randomize_order=True,
        created_by="testadmin",
        usage_count=0
    )
    db_session.add(question)
    db_session.commit()
    db_session.refresh(question)
    return question

@pytest.fixture
def test_question_page_assignment(db_session, test_question_pool, test_page):
    """Create a test question-page assignment"""
    assignment = QuestionPageAssignment(
        question_pool_id=test_question_pool.id,
        page_id=test_page.id,
        order_index=0,
        assigned_by="testadmin"
    )
    db_session.add(assignment)
    db_session.commit()
    db_session.refresh(assignment)
    return assignment

@pytest.fixture
def test_import_log(db_session):
    """Create a test import log"""
    log = ImportLog(
        filename="test_questions.csv",
        import_type="essay",
        total_rows=10,
        successful_imports=8,
        failed_imports=2,
        errors=json.dumps([{"row": 3, "error": "Invalid data"}]),
        imported_by="testadmin"
    )
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)
    return log

@pytest.fixture
def test_question_answers(db_session, test_student_response, test_essay_question, test_slider_question):
    """Create test question answers"""
    essay_answer = QuestionAnswer(
        response_id=test_student_response.id,
        question_id=test_essay_question.id,
        answer_text="I want to become a software engineer and work on innovative projects.",
        answer_value=None,
        answer_json=None
    )
    
    slider_answer = QuestionAnswer(
        response_id=test_student_response.id,
        question_id=test_slider_question.id,
        answer_text=None,
        answer_value=75.0,
        answer_json=None
    )
    
    db_session.add(essay_answer)
    db_session.add(slider_answer)
    db_session.commit()
    db_session.refresh(essay_answer)
    db_session.refresh(slider_answer)
    
    return [essay_answer, slider_answer]

@pytest.fixture
def multiple_pages(db_session):
    """Create multiple test pages"""
    pages = []
    for i in range(3):
        page = Page(
            title=f"Test Page {i+1}",
            description=f"Description for page {i+1}",
            order_index=i,
            is_active=True
        )
        db_session.add(page)
        pages.append(page)
    
    db_session.commit()
    for page in pages:
        db_session.refresh(page)
    
    return pages

@pytest.fixture
def multiple_categories(db_session):
    """Create multiple test categories"""
    categories = []
    category_data = [
        ("Career Planning", "#e74c3c"),
        ("Skills Assessment", "#2ecc71"),
        ("Work Style", "#f39c12")
    ]
    
    for name, color in category_data:
        category = Category(
            name=name,
            description=f"Description for {name}",
            color=color,
            is_active=True
        )
        db_session.add(category)
        categories.append(category)
    
    db_session.commit()
    for category in categories:
        db_session.refresh(category)
    
    return categories

@pytest.fixture
def generate_session_id():
    """Generate a unique session ID"""
    def _generate():
        return str(uuid.uuid4())
    return _generate