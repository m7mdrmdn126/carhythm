import pytest
import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.models.database import Base, get_db
from app.models import Admin, Page, Question, StudentResponse, QuestionAnswer, QuestionType
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
    
    os.close(db_fd)
    os.unlink(db_path)

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
    """Create a test student response"""
    response = StudentResponse(
        session_id="test-session-123",
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
    # Login the admin
    login_response = client.post("/admin/login", data={
        "username": test_admin.username,
        "password": "testpass123"
    })
    
    # Extract session cookie
    cookies = login_response.cookies
    client.cookies = cookies
    
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