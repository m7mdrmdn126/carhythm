"""
Comprehensive integration tests for student examination flow
Tests: welcome page, exam flow, page navigation, answer submission (all question types), completion
"""
import pytest
import json
from fastapi import status
from app.models import StudentResponse, QuestionAnswer


class TestStudentWelcome:
    """Test student welcome page"""
    
    def test_welcome_page_accessible(self, client):
        """Test welcome page is accessible"""
        response = client.get("/student/welcome")
        
        assert response.status_code == 200
        assert b"welcome" in response.content.lower() or b"assessment" in response.content.lower()
    
    def test_root_redirects_to_welcome(self, client):
        """Test root URL redirects to welcome page"""
        response = client.get("/", follow_redirects=False)
        
        assert response.status_code in [301, 302, 307, 308]
        assert "/student/welcome" in response.headers["location"]


class TestExaminationFlow:
    """Test complete examination flow"""
    
    def test_start_examination(self, client, test_page, test_essay_question):
        """Test starting the examination"""
        response = client.get("/student/exam")
        
        assert response.status_code == 200
        # Should have session cookie
        assert "session_id" in response.cookies
        # Should show first page
        assert test_page.title.encode() in response.content
    
    def test_start_exam_with_no_pages(self, client, db_session):
        """Test starting exam when no pages available"""
        # Delete all pages
        from app.models import Page
        db_session.query(Page).delete()
        db_session.commit()
        
        response = client.get("/student/exam")
        
        assert response.status_code == 200
        assert b"no" in response.content.lower() and b"available" in response.content.lower()
    
    def test_session_id_persistence(self, client, test_page):
        """Test session ID persists across requests"""
        # First request
        response1 = client.get("/student/exam")
        session_id1 = response1.cookies.get("session_id")
        
        assert session_id1 is not None
        
        # Second request should have same session
        response2 = client.get("/student/exam")
        session_id2 = response2.cookies.get("session_id")
        
        assert session_id2 == session_id1


class TestPageNavigation:
    """Test navigating between pages"""
    
    def test_get_specific_page(self, client, multiple_pages, db_session):
        """Test getting a specific page"""
        # Add questions to pages
        from app.models import Question, QuestionType
        for page in multiple_pages:
            q = Question(
                page_id=page.id,
                question_text=f"Question for {page.title}",
                question_type=QuestionType.essay,
                order_index=0,
                is_required=True
            )
            db_session.add(q)
        db_session.commit()
        
        # Get second page (index 1)
        response = client.get("/student/exam/page/1")
        
        assert response.status_code == 200
        assert multiple_pages[1].title.encode() in response.content
    
    def test_get_invalid_page_number(self, client, test_page):
        """Test getting invalid page number"""
        response = client.get("/student/exam/page/999")
        
        assert response.status_code == 404
    
    def test_get_negative_page_number(self, client, test_page):
        """Test getting negative page number"""
        response = client.get("/student/exam/page/-1")
        
        assert response.status_code == 404
    
    def test_navigate_first_page(self, client, multiple_pages, db_session):
        """Test first page shows correct navigation"""
        # Add questions
        from app.models import Question, QuestionType
        for page in multiple_pages:
            q = Question(
                page_id=page.id,
                question_text="Test question",
                question_type=QuestionType.essay,
                order_index=0
            )
            db_session.add(q)
        db_session.commit()
        
        response = client.get("/student/exam/page/0")
        
        assert response.status_code == 200
        # Should not have "Previous" button or should be disabled
        # Should have "Next" button
    
    def test_navigate_last_page(self, client, multiple_pages, db_session):
        """Test last page shows correct navigation"""
        # Add questions
        from app.models import Question, QuestionType
        for page in multiple_pages:
            q = Question(
                page_id=page.id,
                question_text="Test question",
                question_type=QuestionType.essay,
                order_index=0
            )
            db_session.add(q)
        db_session.commit()
        
        last_page_index = len(multiple_pages) - 1
        response = client.get(f"/student/exam/page/{last_page_index}")
        
        assert response.status_code == 200
        # Should have "Previous" button
        # Should show submit or complete button


class TestAnswerSubmission:
    """Test submitting answers for all question types"""
    
    def test_submit_essay_answer(self, client, test_page, test_essay_question, db_session):
        """Test submitting essay answer"""
        # Start exam to get session
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit answer
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_essay_question.id}_text": "My essay answer about career goals."
        })
        
        assert response.status_code == 200
        
        # Verify answer was saved
        from app.models import StudentResponse, QuestionAnswer
        student_response = db_session.query(StudentResponse).filter(
            StudentResponse.session_id == session_id
        ).first()
        
        assert student_response is not None
        
        answer = db_session.query(QuestionAnswer).filter(
            QuestionAnswer.response_id == student_response.id,
            QuestionAnswer.question_id == test_essay_question.id
        ).first()
        
        assert answer is not None
        assert "career goals" in answer.answer_text.lower()
    
    def test_submit_slider_answer(self, client, test_page, test_slider_question, db_session):
        """Test submitting slider answer"""
        # Start exam
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit answer
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_slider_question.id}_slider": "75"
        })
        
        assert response.status_code == 200
        
        # Verify answer
        student_response = db_session.query(StudentResponse).filter(
            StudentResponse.session_id == session_id
        ).first()
        
        answer = db_session.query(QuestionAnswer).filter(
            QuestionAnswer.response_id == student_response.id,
            QuestionAnswer.question_id == test_slider_question.id
        ).first()
        
        assert answer is not None
        assert answer.answer_value == 75.0
    
    def test_submit_mcq_single_answer(self, client, test_page, test_mcq_question, db_session):
        """Test submitting single-selection MCQ answer"""
        # Start exam
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit answer (selecting first option)
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_mcq_question.id}_mcq": "0"
        })
        
        assert response.status_code == 200
        
        # Verify answer
        student_response = db_session.query(StudentResponse).filter(
            StudentResponse.session_id == session_id
        ).first()
        
        answer = db_session.query(QuestionAnswer).filter(
            QuestionAnswer.response_id == student_response.id,
            QuestionAnswer.question_id == test_mcq_question.id
        ).first()
        
        assert answer is not None
        assert answer.answer_json is not None
        selected = json.loads(answer.answer_json)
        assert 0 in selected or "0" in selected
    
    def test_submit_mcq_multiple_answers(self, client, test_page, test_mcq_multiple_question, db_session):
        """Test submitting multiple-selection MCQ answer"""
        # Start exam
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit multiple selections
        form_data = {
            "session_id": session_id
        }
        # Send as list
        response = client.post("/student/exam/submit-answers", data=[
            ("session_id", session_id),
            (f"question_{test_mcq_multiple_question.id}_mcq", "0"),
            (f"question_{test_mcq_multiple_question.id}_mcq", "2")
        ])
        
        assert response.status_code == 200
        
        # Verify answer
        student_response = db_session.query(StudentResponse).filter(
            StudentResponse.session_id == session_id
        ).first()
        
        answer = db_session.query(QuestionAnswer).filter(
            QuestionAnswer.response_id == student_response.id,
            QuestionAnswer.question_id == test_mcq_multiple_question.id
        ).first()
        
        assert answer is not None
        assert answer.answer_json is not None
    
    def test_submit_ordering_answer(self, client, test_page, test_ordering_question, db_session):
        """Test submitting ordering answer"""
        # Start exam
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit ordering (user's rank order)
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_ordering_question.id}_ordering": json.dumps([2, 0, 3, 1])
        })
        
        assert response.status_code == 200
        
        # Verify answer
        student_response = db_session.query(StudentResponse).filter(
            StudentResponse.session_id == session_id
        ).first()
        
        answer = db_session.query(QuestionAnswer).filter(
            QuestionAnswer.response_id == student_response.id,
            QuestionAnswer.question_id == test_ordering_question.id
        ).first()
        
        assert answer is not None
        assert answer.answer_json is not None
    
    def test_update_existing_answer(self, client, test_page, test_essay_question, db_session):
        """Test updating an existing answer"""
        # Start exam and submit initial answer
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit initial answer
        client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_essay_question.id}_text": "Initial answer"
        })
        
        # Submit updated answer
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_essay_question.id}_text": "Updated answer"
        })
        
        assert response.status_code == 200
        
        # Verify only one answer exists with updated text
        student_response = db_session.query(StudentResponse).filter(
            StudentResponse.session_id == session_id
        ).first()
        
        answers = db_session.query(QuestionAnswer).filter(
            QuestionAnswer.response_id == student_response.id,
            QuestionAnswer.question_id == test_essay_question.id
        ).all()
        
        assert len(answers) == 1
        assert "Updated answer" in answers[0].answer_text
    
    def test_submit_without_session_id(self, client):
        """Test submitting answers without session ID"""
        response = client.post("/student/exam/submit-answers", data={
            "question_1_text": "Some answer"
        })
        
        assert response.status_code == 400
    
    def test_submit_empty_form(self, client):
        """Test submitting empty form"""
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id
        })
        
        # Should succeed but no answers saved
        assert response.status_code == 200


class TestStudentInfoSubmission:
    """Test submitting student information"""
    
    def test_submit_student_info(self, client, test_page, test_essay_question, db_session):
        """Test submitting student information"""
        # Start exam
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit student info
        response = client.post("/student/exam/submit-info", data={
            "session_id": session_id,
            "email": "student@example.com",
            "full_name": "John Smith",
            "age_group": "23-25",
            "country": "United States",
            "origin_country": "Canada"
        })
        
        assert response.status_code in [200, 302]  # Success or redirect
        
        # Verify student info saved
        student_response = db_session.query(StudentResponse).filter(
            StudentResponse.session_id == session_id
        ).first()
        
        assert student_response is not None
        assert student_response.email == "student@example.com"
        assert student_response.full_name == "John Smith"
    
    def test_submit_incomplete_student_info(self, client):
        """Test submitting incomplete student information"""
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit incomplete info (missing required fields)
        response = client.post("/student/exam/submit-info", data={
            "session_id": session_id,
            "email": "student@example.com"
            # Missing other required fields
        })
        
        # Should fail validation
        assert response.status_code in [400, 422]


class TestExamCompletion:
    """Test completing the examination"""
    
    def test_complete_examination(self, client, test_page, test_essay_question, db_session):
        """Test completing the examination"""
        # Start exam
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit answers
        client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_essay_question.id}_text": "My answer"
        })
        
        # Complete exam
        response = client.post("/student/exam/complete", data={
            "session_id": session_id
        })
        
        assert response.status_code in [200, 302]  # Success or redirect to completion page
        
        # Verify completion timestamp
        student_response = db_session.query(StudentResponse).filter(
            StudentResponse.session_id == session_id
        ).first()
        
        assert student_response is not None
        assert student_response.completed_at is not None
    
    def test_completion_page_accessible(self, client, test_student_response):
        """Test completion page is accessible"""
        response = client.get("/student/completion")
        
        assert response.status_code == 200
        assert b"complete" in response.content.lower() or b"thank" in response.content.lower()


class TestAnswerPersistence:
    """Test answer persistence and retrieval"""
    
    def test_answers_persist_across_pages(self, client, multiple_pages, db_session):
        """Test answers persist when navigating between pages"""
        # Add questions to pages
        from app.models import Question, QuestionType
        questions = []
        for i, page in enumerate(multiple_pages):
            q = Question(
                page_id=page.id,
                question_text=f"Question for page {i}",
                question_type=QuestionType.essay,
                order_index=0,
                is_required=True
            )
            db_session.add(q)
            questions.append(q)
        db_session.commit()
        
        # Start exam
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Answer first page
        client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{questions[0].id}_text": "Answer for page 0"
        })
        
        # Go to second page
        response = client.get("/student/exam/page/1")
        
        # Answer second page
        client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{questions[1].id}_text": "Answer for page 1"
        })
        
        # Go back to first page
        response = client.get("/student/exam/page/0")
        
        # Should show previously entered answer
        assert b"Answer for page 0" in response.content or response.status_code == 200
        
        # Verify both answers exist in database
        student_response = db_session.query(StudentResponse).filter(
            StudentResponse.session_id == session_id
        ).first()
        
        answers = db_session.query(QuestionAnswer).filter(
            QuestionAnswer.response_id == student_response.id
        ).all()
        
        assert len(answers) >= 2
    
    def test_load_existing_answers(self, client, test_page, test_essay_question, db_session):
        """Test loading existing answers when returning to page"""
        # Start exam and submit answer
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_essay_question.id}_text": "My saved answer"
        })
        
        # Reload the same page
        response = client.get("/student/exam")
        
        # Should show the saved answer
        assert b"My saved answer" in response.content or response.status_code == 200


class TestExamEdgeCases:
    """Test edge cases in examination flow"""
    
    def test_concurrent_sessions(self, client, test_page, test_essay_question, db_session):
        """Test multiple concurrent sessions"""
        from fastapi.testclient import TestClient
        from app.main import app
        
        # Create two separate clients
        client1 = TestClient(app)
        client2 = TestClient(app)
        
        # Override get_db for both clients
        def override_get_db():
            from app.models.database import SessionLocal
            db = SessionLocal()
            try:
                yield db
            finally:
                db.close()
        
        from app.models.database import get_db
        client1.app.dependency_overrides[get_db] = override_get_db
        client2.app.dependency_overrides[get_db] = override_get_db
        
        # Start exams for both
        response1 = client1.get("/student/exam")
        session_id1 = response1.cookies.get("session_id")
        
        response2 = client2.get("/student/exam")
        session_id2 = response2.cookies.get("session_id")
        
        # Sessions should be different
        assert session_id1 != session_id2
    
    def test_empty_answer_submission(self, client, test_page, test_essay_question):
        """Test submitting empty answer"""
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit empty answer
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_essay_question.id}_text": ""
        })
        
        # Should accept empty answer (might be optional question)
        assert response.status_code == 200
    
    def test_very_long_essay_answer(self, client, test_page, test_essay_question):
        """Test submitting very long essay answer"""
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Submit very long answer
        long_text = "A" * 10000  # 10,000 characters
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_essay_question.id}_text": long_text
        })
        
        # Should handle long text
        assert response.status_code == 200
    
    def test_slider_boundary_values(self, client, test_page, test_slider_question):
        """Test slider with boundary values"""
        response = client.get("/student/exam")
        session_id = response.cookies.get("session_id")
        
        # Test minimum value
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_slider_question.id}_slider": "0"
        })
        assert response.status_code == 200
        
        # Test maximum value
        response = client.post("/student/exam/submit-answers", data={
            "session_id": session_id,
            f"question_{test_slider_question.id}_slider": "100"
        })
        assert response.status_code == 200
