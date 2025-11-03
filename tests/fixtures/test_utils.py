"""
Test utilities and helper functions
"""

import tempfile
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.database import Base
from app.models import Admin, Page, Question, QuestionType, StudentResponse, QuestionAnswer
from app.utils.security import get_password_hash
from .sample_data import SAMPLE_PAGES, SAMPLE_QUESTIONS, SAMPLE_STUDENTS


def create_test_database():
    """Create a temporary test database"""
    db_fd, db_path = tempfile.mkstemp()
    database_url = f"sqlite:///{db_path}"
    
    engine = create_engine(database_url, connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    Base.metadata.create_all(bind=engine)
    
    return TestingSessionLocal, db_path, db_fd


def cleanup_test_database(db_path, db_fd):
    """Clean up temporary test database"""
    os.close(db_fd)
    os.unlink(db_path)


def populate_test_data(db_session):
    """Populate database with sample test data"""
    
    # Create admin users
    admin1 = Admin(
        username="testadmin",
        password_hash=get_password_hash("testpass123")
    )
    db_session.add(admin1)
    
    # Create pages
    pages = []
    for page_data in SAMPLE_PAGES:
        page = Page(**page_data)
        db_session.add(page)
        pages.append(page)
    
    db_session.commit()
    
    # Create questions
    questions = []
    for question_data in SAMPLE_QUESTIONS:
        # Find the page for this question
        page = next(p for p in pages if p.title == question_data["page_title"])
        
        question_dict = question_data.copy()
        question_dict["page_id"] = page.id
        question_dict["question_type"] = QuestionType(question_dict["question_type"])
        del question_dict["page_title"]
        
        question = Question(**question_dict)
        db_session.add(question)
        questions.append(question)
    
    db_session.commit()
    
    # Create student responses
    responses = []
    for i, student_data in enumerate(SAMPLE_STUDENTS[:2]):  # First 2 students
        response = StudentResponse(
            session_id=f"test-session-{i+1}",
            **student_data
        )
        db_session.add(response)
        responses.append(response)
    
    db_session.commit()
    
    # Create some sample answers
    essay_questions = [q for q in questions if q.question_type == QuestionType.essay]
    slider_questions = [q for q in questions if q.question_type == QuestionType.slider]
    
    essay_answers = [
        "I have a Bachelor's degree in Computer Science with 2 years of experience in software development.",
        "I prefer collaborative environments with opportunities for independent work and continuous learning.",
        "My strongest skills are in Python, JavaScript, and database design. I've built several web applications.",
        "In 5 years, I want to be a senior developer or team lead, specializing in cloud technologies."
    ]
    
    slider_values = [75, 85, 60, 90, 70, 88, 95, 80]
    
    for response in responses:
        # Add essay answers
        for i, question in enumerate(essay_questions[:len(essay_answers)]):
            answer = QuestionAnswer(
                response_id=response.id,
                question_id=question.id,
                answer_text=essay_answers[i],
                answer_value=None
            )
            db_session.add(answer)
        
        # Add slider answers
        for i, question in enumerate(slider_questions[:len(slider_values)]):
            answer = QuestionAnswer(
                response_id=response.id,
                question_id=question.id,
                answer_text=None,
                answer_value=slider_values[i]
            )
            db_session.add(answer)
    
    db_session.commit()
    
    return {
        "admin": admin1,
        "pages": pages,
        "questions": questions,
        "responses": responses
    }


class MockUploadFile:
    """Mock upload file for testing file uploads"""
    
    def __init__(self, filename, content=b"fake file content"):
        self.filename = filename
        self.content = content
        self.file = self.MockFile(content)
    
    class MockFile:
        def __init__(self, content):
            self.content = content
        
        def read(self):
            return self.content


def assert_response_contains(response, expected_strings):
    """Assert that response contains all expected strings"""
    response_text = response.text if hasattr(response, 'text') else str(response.content)
    
    for expected in expected_strings:
        assert expected in response_text, f"Expected '{expected}' not found in response"


def assert_response_redirects(response, expected_location):
    """Assert that response redirects to expected location"""
    assert response.status_code in [301, 302, 303, 307, 308], f"Expected redirect, got {response.status_code}"
    assert response.headers.get("location") == expected_location, f"Expected redirect to '{expected_location}', got '{response.headers.get('location')}'"


def create_test_image_file():
    """Create a mock image file for testing uploads"""
    return MockUploadFile("test.jpg", b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01")


def create_test_invalid_file():
    """Create a mock invalid file for testing uploads"""
    return MockUploadFile("test.txt", b"This is not an image file")


def get_session_from_response(response):
    """Extract session ID from response cookies"""
    return response.cookies.get("session_id")


def login_admin_helper(client, username="testadmin", password="testpass123"):
    """Helper function to login admin and return authenticated client"""
    response = client.post("/admin/login", data={
        "username": username,
        "password": password
    })
    return response.cookies.get("access_token")


def create_test_assessment_flow(db_session):
    """Create a complete test assessment flow with pages, questions, and responses"""
    
    # Create a simple 2-page assessment
    page1 = Page(title="Personal Info", description="Tell us about yourself", order_index=0)
    page2 = Page(title="Goals", description="Share your career goals", order_index=1)
    
    db_session.add(page1)
    db_session.add(page2)
    db_session.commit()
    
    # Add questions
    q1 = Question(
        page_id=page1.id,
        question_text="Describe your background",
        question_type=QuestionType.essay,
        order_index=0,
        is_required=True,
        essay_char_limit=300
    )
    
    q2 = Question(
        page_id=page1.id,
        question_text="Rate your satisfaction",
        question_type=QuestionType.slider,
        order_index=1,
        is_required=True,
        slider_min_label="Low",
        slider_max_label="High"
    )
    
    q3 = Question(
        page_id=page2.id,
        question_text="What are your goals?",
        question_type=QuestionType.essay,
        order_index=0,
        is_required=True,
        essay_char_limit=500
    )
    
    db_session.add(q1)
    db_session.add(q2) 
    db_session.add(q3)
    db_session.commit()
    
    return {
        "pages": [page1, page2],
        "questions": [q1, q2, q3]
    }


def create_sample_csv_content(question_type="essay"):
    """Generate sample CSV content for testing CSV imports"""
    if question_type == "essay":
        return """title,question_text,category_name,is_required,essay_char_limit
Sample Essay 1,What is your career goal?,Career Exploration,TRUE,500
Sample Essay 2,Describe your ideal work environment,Work Style,TRUE,400"""
    
    elif question_type == "slider":
        return """title,question_text,category_name,is_required,slider_min_label,slider_max_label
Sample Slider 1,Rate your leadership interest,Skills Assessment,TRUE,Low,High
Sample Slider 2,How do you rate your communication skills,Skills Assessment,TRUE,Poor,Excellent"""
    
    elif question_type == "mcq":
        return """title,question_text,category_name,is_required,option_1,option_2,option_3,correct_answers,allow_multiple_selection
Sample MCQ 1,What is your work preference?,Work Style,TRUE,Remote,Office,Hybrid,1,FALSE
Sample MCQ 2,Which skills do you have?,Skills Assessment,TRUE,Technical,Leadership,Creative,"1,2",TRUE"""
    
    elif question_type == "ordering":
        return """title,question_text,category_name,is_required,item_1,item_2,item_3,item_4,randomize_order
Sample Ordering 1,Rank these factors,Career Exploration,TRUE,Salary,Growth,Balance,Culture,TRUE
Sample Ordering 2,Prioritize these values,Work Style,TRUE,Impact,Recognition,Stability,Innovation,TRUE"""
    
    return ""


def validate_question_structure(question, expected_type):
    """Validate that a question has the correct structure for its type"""
    assert question.question_text is not None
    assert question.question_type is not None
    assert question.order_index is not None
    
    if expected_type == "essay":
        assert question.essay_char_limit is None or isinstance(question.essay_char_limit, int)
    
    elif expected_type == "slider":
        assert isinstance(question.slider_min_label, (str, type(None)))
        assert isinstance(question.slider_max_label, (str, type(None)))
    
    elif expected_type == "mcq":
        assert question.mcq_options is not None
        assert question.mcq_correct_answer is not None
        assert isinstance(question.allow_multiple_selection, bool)
    
    elif expected_type == "ordering":
        assert question.ordering_options is not None
        assert isinstance(question.randomize_order, bool)


def create_mock_student_session(client, session_id=None):
    """Create a mock student session with session ID"""
    import uuid
    if session_id is None:
        session_id = str(uuid.uuid4())
    
    # Set session cookie
    client.cookies.set("session_id", session_id)
    return session_id


def compare_dict_subset(actual, expected):
    """Compare that actual dict contains all key-value pairs from expected dict"""
    for key, value in expected.items():
        assert key in actual, f"Key '{key}' not found in actual dict"
        assert actual[key] == value, f"Value mismatch for key '{key}': expected {value}, got {actual[key]}"


def create_bulk_test_data(db_session, num_pages=3, num_questions_per_page=5):
    """Create bulk test data for performance testing"""
    import json
    
    pages = []
    questions = []
    
    for i in range(num_pages):
        page = Page(
            title=f"Test Page {i+1}",
            description=f"Description for page {i+1}",
            order_index=i,
            is_active=True
        )
        db_session.add(page)
        pages.append(page)
    
    db_session.commit()
    
    question_types = [QuestionType.essay, QuestionType.slider, QuestionType.mcq, QuestionType.ordering]
    
    for page in pages:
        for j in range(num_questions_per_page):
            q_type = question_types[j % len(question_types)]
            
            question_data = {
                "page_id": page.id,
                "question_text": f"Question {j+1} for {page.title}",
                "question_type": q_type,
                "order_index": j,
                "is_required": True
            }
            
            if q_type == QuestionType.essay:
                question_data["essay_char_limit"] = 500
            elif q_type == QuestionType.slider:
                question_data["slider_min_label"] = "Low"
                question_data["slider_max_label"] = "High"
            elif q_type == QuestionType.mcq:
                question_data["mcq_options"] = json.dumps(["Option A", "Option B", "Option C"])
                question_data["mcq_correct_answer"] = json.dumps([0])
                question_data["allow_multiple_selection"] = False
            elif q_type == QuestionType.ordering:
                question_data["ordering_options"] = json.dumps(["Item 1", "Item 2", "Item 3"])
                question_data["randomize_order"] = True
            
            question = Question(**question_data)
            db_session.add(question)
            questions.append(question)
    
    db_session.commit()
    
    return {"pages": pages, "questions": questions}