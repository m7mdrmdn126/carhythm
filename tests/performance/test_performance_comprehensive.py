"""
Performance and load testing for the CaRhythm system
Tests system behavior under various load conditions
"""

import pytest
import time
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime


class TestDatabasePerformance:
    """Test database query performance"""
    
    def test_bulk_question_retrieval(self, db_session, multiple_pages):
        """Test retrieving questions for multiple pages"""
        from app.services.question_service import get_questions_by_page
        
        start_time = time.time()
        
        for page in multiple_pages:
            questions = get_questions_by_page(db_session, page.id)
        
        elapsed_time = time.time() - start_time
        
        # Should complete quickly
        assert elapsed_time < 1.0  # Less than 1 second for 3 pages
    
    def test_large_response_query(self, db_session):
        """Test querying large number of responses"""
        from app.models import StudentResponse
        from app.services.response_service import get_all_responses
        
        # Create multiple responses
        for i in range(20):
            response = StudentResponse(
                session_id=str(uuid.uuid4()),
                email=f"perf{i}@test.com",
                full_name=f"Performance Test {i}",
                age_group="19-22",
                country="USA",
                origin_country="USA"
            )
            db_session.add(response)
        
        db_session.commit()
        
        start_time = time.time()
        responses = get_all_responses(db_session)
        elapsed_time = time.time() - start_time
        
        assert len(responses) >= 20
        assert elapsed_time < 2.0  # Should be fast
    
    def test_category_question_join(self, db_session, test_category, multiple_categories):
        """Test performance of category-question joins"""
        from app.services.question_pool_service import QuestionPoolService
        from app.models import QuestionPool
        
        # Create multiple pool questions
        for i in range(10):
            question = QuestionPool(
                title=f"Perf Question {i}",
                question_text=f"Performance test question {i}",
                question_type="essay",
                category_id=test_category.id,
                is_required=True,
                created_by="perftest"
            )
            db_session.add(question)
        
        db_session.commit()
        
        start_time = time.time()
        questions = QuestionPoolService.get_questions_pool(db_session)
        elapsed_time = time.time() - start_time
        
        assert len(questions) >= 10
        assert elapsed_time < 1.0


class TestAPIPerformance:
    """Test API endpoint performance"""
    
    def test_dashboard_load_time(self, authenticated_admin_client):
        """Test admin dashboard load time"""
        start_time = time.time()
        response = authenticated_admin_client.get("/admin/dashboard")
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 2.0  # Should load within 2 seconds
    
    def test_results_page_load(self, authenticated_admin_client):
        """Test results page load time"""
        start_time = time.time()
        response = authenticated_admin_client.get("/admin/results")
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 2.0
    
    def test_question_pool_load(self, authenticated_admin_client):
        """Test question pool page load time"""
        start_time = time.time()
        response = authenticated_admin_client.get("/admin/question-pool")
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 2.0
    
    def test_api_modules_response_time(self, client):
        """Test API v2 modules endpoint response time"""
        start_time = time.time()
        response = client.get("/api/v2/modules")
        elapsed_time = time.time() - start_time
        
        assert response.status_code == 200
        assert elapsed_time < 1.0  # API should be very fast


class TestScoringPerformance:
    """Test scoring calculation performance"""
    
    def test_riasec_calculation_speed(self, db_session, test_student_response):
        """Test RIASEC score calculation performance"""
        from app.services.scoring_service_v1_1 import calculate_riasec_scores_v1_1
        from app.models import Question, QuestionAnswer, QuestionType
        from app.models import Page
        
        # Create test page
        page = Page(title="Perf Test Page", order_index=1, is_active=True)
        db_session.add(page)
        db_session.commit()
        
        # Create multiple questions with holland codes
        holland_codes = ["R", "I", "A", "S", "E", "C"] * 5  # 30 questions
        
        for i, code in enumerate(holland_codes):
            question = Question(
                page_id=page.id,
                question_text=f"Question {i}",
                question_type=QuestionType.slider,
                holland_code=code,
                order_index=i,
                is_required=True
            )
            db_session.add(question)
            db_session.flush()
            
            # Add answer
            answer = QuestionAnswer(
                response_id=test_student_response.id,
                question_id=question.id,
                answer_value=float(50 + i)
            )
            db_session.add(answer)
        
        db_session.commit()
        
        start_time = time.time()
        scores = calculate_riasec_scores_v1_1(db_session, test_student_response.id)
        elapsed_time = time.time() - start_time
        
        assert isinstance(scores, dict)
        assert elapsed_time < 1.0  # Should calculate quickly
    
    def test_complete_profile_calculation(self, db_session, test_student_response):
        """Test complete profile calculation performance"""
        from app.services.scoring_service_v1_1 import calculate_complete_profile_v1_1
        
        start_time = time.time()
        profile = calculate_complete_profile_v1_1(db_session, test_student_response.id)
        elapsed_time = time.time() - start_time
        
        assert isinstance(profile, dict)
        assert elapsed_time < 2.0  # Complete calculation should be fast


class TestPDFGenerationPerformance:
    """Test PDF generation performance"""
    
    def test_pdf_generation_speed(self):
        """Test PDF generation time"""
        from app.services.pdf_service import generate_pdf_report
        
        response_data = {
            'student_name': 'Performance Test',
            'student_email': 'perf@test.com',
            'session_id': 'perf-session'
        }
        
        scores_data = {
            'holland_code': 'RIA',
            'riasec_raw_scores': {'R': 12, 'I': 10, 'A': 8, 'S': 6, 'E': 4, 'C': 2},
            'bigfive_raw_scores': {'O': 20, 'C': 18, 'E': 15, 'A': 16, 'N': 10},
            'behavioral_raw_scores': {'motivation': 12, 'grit': 11},
            'bigfive_strength_labels': {'O': 'High', 'C': 'High', 'E': 'Medium', 'A': 'High', 'N': 'Low'},
            'behavioral_strength_labels': {'motivation': 'High', 'grit': 'High'},
            'behavioral_flags': {},
            'ikigai_zones': {}
        }
        
        start_time = time.time()
        pdf_buffer = generate_pdf_report(response_data, scores_data, is_free_version=True)
        elapsed_time = time.time() - start_time
        
        assert pdf_buffer is not None
        assert elapsed_time < 5.0  # PDF generation should complete within 5 seconds
    
    def test_radar_chart_generation_speed(self):
        """Test radar chart generation time"""
        from app.services.pdf_service import create_riasec_radar_chart
        
        riasec_scores = {'R': 12, 'I': 10, 'A': 8, 'S': 6, 'E': 4, 'C': 2}
        
        start_time = time.time()
        chart_buffer = create_riasec_radar_chart(riasec_scores)
        elapsed_time = time.time() - start_time
        
        assert chart_buffer is not None
        assert elapsed_time < 2.0  # Chart generation should be fast


class TestConcurrentOperations:
    """Test system under concurrent load"""
    
    def test_concurrent_session_creation(self, db_session):
        """Test creating multiple sessions concurrently"""
        from app.models import StudentResponse
        
        def create_session(index):
            session = StudentResponse(
                session_id=str(uuid.uuid4()),
                email=f"concurrent{index}@test.com",
                full_name=f"Concurrent User {index}",
                age_group="19-22",
                country="USA",
                origin_country="USA"
            )
            db_session.add(session)
            db_session.commit()
            return session.id
        
        start_time = time.time()
        
        # Create 10 sessions concurrently
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(create_session, i) for i in range(10)]
            results = [f.result() for f in futures]
        
        elapsed_time = time.time() - start_time
        
        assert len(results) == 10
        assert elapsed_time < 5.0  # Should handle concurrent operations
    
    def test_concurrent_answer_submission(self, db_session, test_student_response, test_slider_question):
        """Test submitting multiple answers concurrently"""
        from app.models import QuestionAnswer, Question, QuestionType, Page
        
        # Create test page
        page = Page(title="Concurrent Test", order_index=1, is_active=True)
        db_session.add(page)
        db_session.commit()
        
        # Create multiple questions
        questions = []
        for i in range(10):
            q = Question(
                page_id=page.id,
                question_text=f"Concurrent Q{i}",
                question_type=QuestionType.slider,
                order_index=i,
                is_required=True
            )
            db_session.add(q)
            questions.append(q)
        
        db_session.commit()
        
        def submit_answer(question_id):
            answer = QuestionAnswer(
                response_id=test_student_response.id,
                question_id=question_id,
                answer_value=75.0
            )
            db_session.add(answer)
            db_session.commit()
            return answer.id
        
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(submit_answer, q.id) for q in questions]
            results = [f.result() for f in futures]
        
        elapsed_time = time.time() - start_time
        
        assert len(results) == 10
        assert elapsed_time < 5.0


class TestMemoryUsage:
    """Test memory efficiency"""
    
    def test_large_dataset_handling(self, db_session):
        """Test handling large number of records"""
        from app.models import QuestionPool
        
        # Create many pool questions
        for i in range(100):
            question = QuestionPool(
                title=f"Memory Test {i}",
                question_text=f"Question {i} for memory testing",
                question_type="essay",
                is_required=False,
                created_by="memtest"
            )
            db_session.add(question)
            
            if i % 20 == 0:  # Commit in batches
                db_session.commit()
        
        db_session.commit()
        
        # Query all questions
        start_time = time.time()
        questions = db_session.query(QuestionPool).all()
        elapsed_time = time.time() - start_time
        
        assert len(questions) >= 100
        assert elapsed_time < 3.0  # Should handle large queries


class TestCachingEfficiency:
    """Test caching and query optimization"""
    
    def test_repeated_page_queries(self, db_session, test_page):
        """Test efficiency of repeated queries"""
        from app.services.question_service import get_page_by_id
        
        # First query
        start_time = time.time()
        page1 = get_page_by_id(db_session, test_page.id)
        first_query_time = time.time() - start_time
        
        # Subsequent queries (should be faster due to SQLAlchemy caching)
        start_time = time.time()
        for _ in range(10):
            page = get_page_by_id(db_session, test_page.id)
        repeated_queries_time = time.time() - start_time
        
        assert page1 is not None
        # Repeated queries should not be significantly slower
        assert repeated_queries_time < first_query_time * 15  # Some tolerance
    
    def test_eager_loading_performance(self, db_session, test_page, test_essay_question):
        """Test eager loading vs lazy loading performance"""
        from app.models import Page
        from sqlalchemy.orm import joinedload
        
        # Lazy loading
        start_time = time.time()
        page = db_session.query(Page).filter(Page.id == test_page.id).first()
        _ = page.questions  # Triggers lazy load
        lazy_time = time.time() - start_time
        
        # Clear session
        db_session.expunge_all()
        
        # Eager loading
        start_time = time.time()
        page = db_session.query(Page).options(joinedload(Page.questions)).filter(Page.id == test_page.id).first()
        _ = page.questions
        eager_time = time.time() - start_time
        
        # Both should be reasonably fast
        assert lazy_time < 1.0
        assert eager_time < 1.0


class TestScalability:
    """Test system scalability"""
    
    def test_pagination_performance(self, db_session):
        """Test pagination with large datasets"""
        from app.models import StudentResponse
        
        # Create many responses
        for i in range(50):
            response = StudentResponse(
                session_id=str(uuid.uuid4()),
                email=f"scale{i}@test.com",
                full_name=f"Scale Test {i}",
                age_group="19-22",
                country="USA",
                origin_country="USA"
            )
            db_session.add(response)
        
        db_session.commit()
        
        # Test paginated queries
        page_size = 10
        start_time = time.time()
        
        for page_num in range(5):  # 5 pages
            offset = page_num * page_size
            page_data = db_session.query(StudentResponse).limit(page_size).offset(offset).all()
            assert len(page_data) <= page_size
        
        elapsed_time = time.time() - start_time
        
        assert elapsed_time < 2.0  # Pagination should be efficient
    
    def test_filtered_query_performance(self, db_session, test_category, multiple_categories):
        """Test performance of filtered queries"""
        from app.services.question_pool_service import QuestionPoolService
        from app.schemas.question_pool import QuestionPoolFilter
        from app.models import QuestionPool
        
        # Create questions in different categories
        for cat in multiple_categories[:2]:
            for i in range(10):
                question = QuestionPool(
                    title=f"Filter Test {cat.name} {i}",
                    question_text=f"Question {i}",
                    question_type="essay",
                    category_id=cat.id,
                    is_required=True,
                    created_by="filtertest"
                )
                db_session.add(question)
        
        db_session.commit()
        
        # Test filtered query
        start_time = time.time()
        filters = QuestionPoolFilter(
            category_id=multiple_categories[0].id,
            skip=0,
            limit=20
        )
        questions = QuestionPoolService.get_questions_pool(db_session, filters)
        elapsed_time = time.time() - start_time
        
        assert len(questions) >= 0
        assert elapsed_time < 1.0  # Filtered queries should be fast
