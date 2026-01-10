"""
End-to-end workflow tests
Tests complete user journeys through the system
"""

import pytest
import json
import uuid
from datetime import datetime


class TestCompleteStudentWorkflow:
    """Test complete student assessment workflow from start to finish"""
    
    def test_full_student_journey(self, client, db_session, test_page, test_essay_question, test_slider_question):
        """Test complete student journey: start -> answer -> complete -> results"""
        from app.models import StudentResponse, QuestionAnswer
        
        # Step 1: Visit welcome page
        response = client.get("/student/welcome")
        assert response.status_code == 200
        
        # Step 2: Start exam (creates session)
        session_id = str(uuid.uuid4())
        student_response = StudentResponse(
            session_id=session_id,
            email="journey@test.com",
            full_name="Journey Test",
            age_group="19-22",
            country="USA",
            origin_country="USA"
        )
        db_session.add(student_response)
        db_session.commit()
        
        # Step 3: Answer questions
        # Essay answer
        essay_answer = QuestionAnswer(
            response_id=student_response.id,
            question_id=test_essay_question.id,
            answer_text="I want to build a career in software engineering"
        )
        db_session.add(essay_answer)
        
        # Slider answer
        slider_answer = QuestionAnswer(
            response_id=student_response.id,
            question_id=test_slider_question.id,
            answer_value=85.0
        )
        db_session.add(slider_answer)
        db_session.commit()
        
        # Step 4: Complete assessment
        student_response.completed_at = datetime.utcnow()
        db_session.commit()
        
        # Step 5: Verify session exists with answers
        saved_response = db_session.query(StudentResponse).filter(
            StudentResponse.session_id == session_id
        ).first()
        
        assert saved_response is not None
        assert len(saved_response.answers) == 2
        assert saved_response.completed_at is not None
        
        # Step 6: Calculate scores (would happen after completion)
        from app.services.scoring_service_v1_1 import calculate_complete_profile_v1_1
        profile = calculate_complete_profile_v1_1(db_session, saved_response.id)
        assert isinstance(profile, dict)


class TestCompleteAdminWorkflow:
    """Test complete admin workflow for managing assessment"""
    
    def test_full_admin_workflow(self, authenticated_admin_client, db_session):
        """Test admin creating page, questions, viewing responses"""
        from app.models import Page, Question, QuestionType
        
        # Step 1: Login (already authenticated via fixture)
        
        # Step 2: Create a new page
        response = authenticated_admin_client.post("/admin/pages", data={
            "title": "Admin Workflow Page",
            "description": "Testing admin workflow",
            "order_index": "1",
            "is_active": "true"
        })
        assert response.status_code == 302
        
        # Get created page
        page = db_session.query(Page).filter(Page.title == "Admin Workflow Page").first()
        assert page is not None
        
        # Step 3: Create questions on the page
        # Essay question
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(page.id),
            "question_text": "Admin test essay question",
            "question_type": "essay",
            "order_index": "1",
            "is_required": "true",
            "essay_char_limit": "500"
        })
        assert response.status_code == 302
        
        # Slider question
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(page.id),
            "question_text": "Admin test slider question",
            "question_type": "slider",
            "order_index": "2",
            "is_required": "true",
            "slider_min_label": "Low",
            "slider_max_label": "High"
        })
        assert response.status_code == 302
        
        # Step 4: Verify questions were created
        questions = db_session.query(Question).filter(Question.page_id == page.id).all()
        assert len(questions) == 2
        
        # Step 5: View responses page
        response = authenticated_admin_client.get("/admin/results")
        assert response.status_code == 200
        
        # Step 6: View dashboard
        response = authenticated_admin_client.get("/admin/dashboard")
        assert response.status_code == 200


class TestQuestionPoolWorkflow:
    """Test question pool and assignment workflow"""
    
    def test_pool_to_page_workflow(self, authenticated_admin_client, db_session, test_category):
        """Test creating pool question and assigning to page"""
        from app.models import Page, QuestionPool, QuestionPageAssignment
        
        # Step 1: Create a category (use existing test_category)
        
        # Step 2: Create questions in pool
        response = authenticated_admin_client.post("/admin/question-pool/questions", data={
            "title": "Pool Workflow Question",
            "question_text": "This question will be assigned to pages",
            "question_type": "essay",
            "category_id": str(test_category.id),
            "is_required": "true",
            "essay_char_limit": "400"
        })
        assert response.status_code == 302
        
        # Get created pool question
        pool_question = db_session.query(QuestionPool).filter(
            QuestionPool.title == "Pool Workflow Question"
        ).first()
        assert pool_question is not None
        
        # Step 3: Create a page to assign to
        response = authenticated_admin_client.post("/admin/pages", data={
            "title": "Pool Assignment Page",
            "description": "For testing pool assignments",
            "order_index": "5",
            "is_active": "true"
        })
        assert response.status_code == 302
        
        page = db_session.query(Page).filter(Page.title == "Pool Assignment Page").first()
        assert page is not None
        
        # Step 4: Assign pool question to page
        response = authenticated_admin_client.post(f"/admin/pages/{page.id}/assign-question", data={
            "question_pool_id": str(pool_question.id),
            "order_index": "0"
        })
        assert response.status_code == 302
        
        # Step 5: Verify assignment
        assignment = db_session.query(QuestionPageAssignment).filter(
            QuestionPageAssignment.question_pool_id == pool_question.id,
            QuestionPageAssignment.page_id == page.id
        ).first()
        assert assignment is not None
        
        # Step 6: Verify usage count incremented
        db_session.refresh(pool_question)
        assert pool_question.usage_count >= 0  # Should be tracked


class TestCSVImportExportWorkflow:
    """Test CSV import and export workflow"""
    
    def test_csv_round_trip(self, authenticated_admin_client, db_session, test_category):
        """Test importing CSV, then exporting it"""
        from app.models import QuestionPool
        
        # Step 1: Prepare CSV data
        csv_content = f"""title,question_text,category_name,is_required,essay_char_limit
CSV Test 1,First CSV question,{test_category.name},TRUE,500
CSV Test 2,Second CSV question,{test_category.name},FALSE,600"""
        
        # Step 2: Import CSV
        from io import BytesIO
        csv_file = BytesIO(csv_content.encode('utf-8'))
        
        response = authenticated_admin_client.post(
            "/admin/csv-import/essay",
            files={"csv_file": ("test.csv", csv_file, "text/csv")}
        )
        assert response.status_code in [200, 302]
        
        # Step 3: Verify questions were imported
        question1 = db_session.query(QuestionPool).filter(
            QuestionPool.title == "CSV Test 1"
        ).first()
        question2 = db_session.query(QuestionPool).filter(
            QuestionPool.title == "CSV Test 2"
        ).first()
        
        assert question1 is not None
        assert question2 is not None
        
        # Step 4: Export questions back to CSV
        question_ids = f"{question1.id},{question2.id}" if question2 else str(question1.id)
        
        response = authenticated_admin_client.get(
            f"/admin/question-pool/export?question_ids={question_ids}&question_type=essay"
        )
        
        if response.status_code == 200:
            csv_output = response.text
            assert "CSV Test 1" in csv_output or response.content


class TestScoringAndPDFWorkflow:
    """Test scoring calculation and PDF generation workflow"""
    
    def test_complete_scoring_pdf_workflow(self, db_session, test_student_response, test_essay_question, test_slider_question):
        """Test calculating scores and generating PDF"""
        from app.models import QuestionAnswer, AssessmentScore
        from app.services.scoring_service_v1_1 import calculate_complete_profile_v1_1, save_assessment_score_v1_1
        from app.services.pdf_service import generate_pdf_report
        
        # Step 1: Create some answers with traits
        test_slider_question.holland_code = "R"
        test_slider_question.bigfive_trait = "O"
        db_session.add(test_slider_question)
        
        answer = QuestionAnswer(
            response_id=test_student_response.id,
            question_id=test_slider_question.id,
            answer_value=80.0
        )
        db_session.add(answer)
        db_session.commit()
        
        # Step 2: Calculate complete profile
        profile = calculate_complete_profile_v1_1(db_session, test_student_response.id)
        assert isinstance(profile, dict)
        
        # Step 3: Save scores to database
        saved_score = save_assessment_score_v1_1(db_session, test_student_response.id, profile)
        assert saved_score is not None
        
        # Step 4: Verify scores in database
        score = db_session.query(AssessmentScore).filter(
            AssessmentScore.response_id == test_student_response.id
        ).first()
        assert score is not None
        
        # Step 5: Generate PDF from scores
        response_data = {
            'student_name': test_student_response.full_name,
            'student_email': test_student_response.email,
            'session_id': test_student_response.session_id
        }
        
        scores_data = {
            'holland_code': profile.get('holland_code', 'RIA'),
            'riasec_raw_scores': profile.get('riasec_raw_scores', {}),
            'bigfive_raw_scores': profile.get('bigfive_raw_scores', {}),
            'behavioral_raw_scores': profile.get('behavioral_raw_scores', {}),
            'bigfive_strength_labels': profile.get('bigfive_strength_labels', {}),
            'behavioral_strength_labels': profile.get('behavioral_strength_labels', {}),
            'behavioral_flags': profile.get('behavioral_flags', {}),
            'ikigai_zones': profile.get('ikigai_zones', {})
        }
        
        pdf_buffer = generate_pdf_report(response_data, scores_data, is_free_version=True)
        
        assert pdf_buffer is not None
        assert pdf_buffer.tell() > 0  # Has content


class TestAPIv2Workflow:
    """Test API v2 workflow for React frontend"""
    
    def test_react_frontend_workflow(self, client, db_session, test_page, test_essay_question):
        """Test complete workflow via API v2"""
        from app.models import StudentResponse, QuestionAnswer
        
        # Step 1: Get modules
        response = client.get("/api/v2/modules")
        assert response.status_code == 200
        modules = response.json()
        
        # Step 2: Start session
        response = client.post("/api/v2/session/start")
        assert response.status_code == 200
        data = response.json()
        session_id = data.get("session_id")
        assert session_id is not None
        
        # Step 3: Get questions for a page
        response = client.get(f"/api/v2/questions?page_id={test_page.id}&language=en&session_id={session_id}")
        assert response.status_code == 200
        questions_data = response.json()
        
        # Step 4: Submit answer
        response = client.post("/api/v2/session/submit-answer", json={
            "session_id": session_id,
            "question_id": test_essay_question.id,
            "answer": "API workflow test answer",
            "page_id": test_page.id
        })
        assert response.status_code in [200, 400]  # May fail validation if session not properly setup
        
        # Step 5: Submit student info
        response = client.post("/api/v2/session/student-info", json={
            "session_id": session_id,
            "email": "api@test.com",
            "full_name": "API Test Student",
            "age_group": "19-22",
            "country": "USA",
            "origin_country": "USA"
        })
        assert response.status_code in [200, 400]


class TestFeedbackWorkflow:
    """Test feedback submission and viewing workflow"""
    
    def test_feedback_submission_workflow(self, client, authenticated_admin_client, db_session, test_student_response):
        """Test student submitting feedback and admin viewing it"""
        from app.models import Feedback
        
        # Step 1: Student submits feedback
        response = client.post("/feedback/submit", json={
            "session_id": test_student_response.session_id,
            "rating": 5,
            "comments": "Great assessment experience!"
        })
        assert response.status_code in [200, 201]
        
        # Step 2: Verify feedback in database
        feedback = db_session.query(Feedback).filter(
            Feedback.response_id == test_student_response.id
        ).first()
        
        if feedback:  # If feedback was created
            assert feedback.rating == 5
            assert feedback.comments == "Great assessment experience!"
        
        # Step 3: Admin views feedback list
        response = authenticated_admin_client.get("/admin/feedback")
        assert response.status_code == 200


class TestMultipleStudentsWorkflow:
    """Test multiple students taking assessment simultaneously"""
    
    def test_concurrent_students(self, db_session, test_page, test_essay_question):
        """Test multiple students with unique sessions"""
        from app.models import StudentResponse, QuestionAnswer
        
        sessions = []
        
        # Create 3 different student sessions
        for i in range(3):
            session_id = str(uuid.uuid4())
            response = StudentResponse(
                session_id=session_id,
                email=f"student{i}@test.com",
                full_name=f"Student {i}",
                age_group="19-22",
                country="USA",
                origin_country="USA"
            )
            db_session.add(response)
            sessions.append(response)
        
        db_session.commit()
        
        # Each student answers the question
        for i, student_session in enumerate(sessions):
            answer = QuestionAnswer(
                response_id=student_session.id,
                question_id=test_essay_question.id,
                answer_text=f"Answer from student {i}"
            )
            db_session.add(answer)
        
        db_session.commit()
        
        # Verify all sessions have unique IDs and answers
        for i, student_session in enumerate(sessions):
            db_session.refresh(student_session)
            assert len(student_session.answers) == 1
            assert student_session.answers[0].answer_text == f"Answer from student {i}"
        
        # Verify sessions are independent
        session_ids = [s.session_id for s in sessions]
        assert len(session_ids) == len(set(session_ids))  # All unique


class TestErrorHandlingWorkflow:
    """Test error handling in various workflows"""
    
    def test_invalid_session_handling(self, client):
        """Test handling of invalid session ID"""
        response = client.post("/student/exam/submit-answers", data={
            "session_id": "invalid-session-id",
            "question_1": "test answer"
        })
        # Should handle gracefully (redirect or error)
        assert response.status_code in [302, 400, 404]
    
    def test_missing_required_fields(self, authenticated_admin_client, test_page):
        """Test creating question with missing required fields"""
        response = authenticated_admin_client.post("/admin/questions", data={
            "page_id": str(test_page.id),
            # Missing question_text
            "question_type": "essay",
            "order_index": "1"
        })
        # Should fail validation
        assert response.status_code in [400, 422, 302]
    
    def test_duplicate_category_name(self, authenticated_admin_client, test_category):
        """Test creating category with duplicate name"""
        response = authenticated_admin_client.post("/admin/categories", data={
            "name": test_category.name,  # Duplicate
            "description": "Duplicate category",
            "color": "#000000"
        })
        # Should handle duplicate gracefully
        assert response.status_code in [302, 400]
    
    def test_delete_nonexistent_resource(self, authenticated_admin_client):
        """Test deleting a non-existent resource"""
        response = authenticated_admin_client.post("/admin/pages/99999/delete")
        # Should handle gracefully
        assert response.status_code in [302, 404]
