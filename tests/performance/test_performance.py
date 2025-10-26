"""
Performance and load testing for the Career DNA Assessment application
"""

import time
import statistics
import pytest
from concurrent.futures import ThreadPoolExecutor
from fastapi.testclient import TestClient
from app.main import app


class TestPerformance:
    """Performance tests for critical application endpoints"""
    
    def setup_method(self):
        self.client = TestClient(app)
    
    @pytest.mark.slow
    def test_homepage_load_time(self):
        """Test homepage loads within acceptable time"""
        start_time = time.time()
        response = self.client.get("/")
        end_time = time.time()
        
        load_time = end_time - start_time
        
        assert response.status_code == 200
        assert load_time < 1.0, f"Homepage load time {load_time:.2f}s exceeds 1 second threshold"
    
    @pytest.mark.slow
    def test_admin_dashboard_load_time(self, authenticated_admin_client):
        """Test admin dashboard loads within acceptable time"""
        start_time = time.time()
        response = authenticated_admin_client.get("/admin/dashboard")
        end_time = time.time()
        
        load_time = end_time - start_time
        
        assert response.status_code == 200
        assert load_time < 2.0, f"Admin dashboard load time {load_time:.2f}s exceeds 2 second threshold"
    
    @pytest.mark.slow
    def test_examination_page_load_time(self, populated_db):
        """Test examination page loads within acceptable time"""
        start_time = time.time()
        response = self.client.get("/examination")
        end_time = time.time()
        
        load_time = end_time - start_time
        
        assert response.status_code == 200
        assert load_time < 1.5, f"Examination page load time {load_time:.2f}s exceeds 1.5 second threshold"
    
    @pytest.mark.slow
    def test_concurrent_homepage_requests(self):
        """Test homepage can handle concurrent requests"""
        def make_request():
            response = self.client.get("/")
            return response.status_code == 200
        
        # Test 10 concurrent requests
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request) for _ in range(10)]
            results = [future.result() for future in futures]
        
        # All requests should succeed
        assert all(results), "Some concurrent requests failed"
    
    @pytest.mark.slow
    def test_examination_answer_submission_performance(self, populated_db):
        """Test examination answer submission performance"""
        # Start examination
        start_response = self.client.post("/examination/start")
        assert start_response.status_code == 302
        
        session_id = start_response.cookies.get("session_id")
        
        # Submit answers for first page
        times = []
        for i in range(5):  # Submit 5 times to get average
            start_time = time.time()
            
            response = self.client.post(
                "/examination/submit_answers",
                data={
                    "session_id": session_id,
                    "page_id": "1",
                    "answers": '{"1": {"type": "essay", "value": "Test answer for performance testing"}, "2": {"type": "slider", "value": 75}}'
                }
            )
            
            end_time = time.time()
            times.append(end_time - start_time)
            
            assert response.status_code == 302
        
        avg_time = statistics.mean(times)
        assert avg_time < 0.5, f"Answer submission average time {avg_time:.2f}s exceeds 0.5 second threshold"
    
    @pytest.mark.slow
    def test_results_page_performance(self, populated_db):
        """Test results page performance with multiple student responses"""
        # Create multiple test responses first
        for i in range(20):
            start_response = self.client.post("/examination/start")
            session_id = start_response.cookies.get("session_id")
            
            # Submit student info
            self.client.post("/examination/submit_student_info", data={
                "session_id": session_id,
                "name": f"Test Student {i}",
                "email": f"student{i}@test.com",
                "phone": f"555-000{i:04d}",
                "age": "25",
                "education": "Bachelor's",
                "experience": "2-5 years"
            })
        
        # Now test results page performance
        start_time = time.time()
        response = self.client.get("/admin/results")
        end_time = time.time()
        
        load_time = end_time - start_time
        
        assert response.status_code == 200
        assert load_time < 3.0, f"Results page load time {load_time:.2f}s exceeds 3 second threshold with 20 responses"


class TestLoadTesting:
    """Load testing scenarios"""
    
    def setup_method(self):
        self.client = TestClient(app)
    
    @pytest.mark.slow
    def test_sustained_load_homepage(self):
        """Test homepage under sustained load"""
        def make_requests(num_requests=50):
            success_count = 0
            for _ in range(num_requests):
                try:
                    response = self.client.get("/")
                    if response.status_code == 200:
                        success_count += 1
                except Exception:
                    pass
            return success_count
        
        # Simulate sustained load with multiple threads
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(make_requests, 20) for _ in range(5)]
            results = [future.result() for future in futures]
        
        total_requests = 5 * 20  # 5 threads * 20 requests each
        total_success = sum(results)
        success_rate = total_success / total_requests
        
        assert success_rate >= 0.95, f"Success rate {success_rate:.2%} is below 95% threshold under load"
    
    @pytest.mark.slow
    def test_examination_flow_under_load(self, populated_db):
        """Test complete examination flow under load"""
        def complete_examination():
            try:
                # Start examination
                start_response = self.client.post("/examination/start")
                if start_response.status_code != 302:
                    return False
                
                session_id = start_response.cookies.get("session_id")
                
                # Submit answers for first page
                answer_response = self.client.post(
                    "/examination/submit_answers",
                    data={
                        "session_id": session_id,
                        "page_id": "1",
                        "answers": '{"1": {"type": "essay", "value": "Load test answer"}, "2": {"type": "slider", "value": 80}}'
                    }
                )
                
                if answer_response.status_code != 302:
                    return False
                
                # Submit student info
                info_response = self.client.post("/examination/submit_student_info", data={
                    "session_id": session_id,
                    "name": "Load Test Student",
                    "email": "loadtest@test.com",
                    "phone": "555-0000",
                    "age": "25",
                    "education": "Bachelor's",
                    "experience": "2-5 years"
                })
                
                return info_response.status_code == 200
                
            except Exception:
                return False
        
        # Run 10 concurrent examination flows
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(complete_examination) for _ in range(10)]
            results = [future.result() for future in futures]
        
        success_rate = sum(results) / len(results)
        assert success_rate >= 0.9, f"Examination flow success rate {success_rate:.2%} is below 90% under load"


class TestMemoryUsage:
    """Memory usage and resource management tests"""
    
    @pytest.mark.slow
    def test_memory_usage_examination_session(self, populated_db):
        """Test memory doesn't leak during examination sessions"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        # Create and complete multiple examination sessions
        for i in range(10):
            client = TestClient(app)
            
            # Start examination
            start_response = client.post("/examination/start")
            session_id = start_response.cookies.get("session_id")
            
            # Submit answers
            client.post(
                "/examination/submit_answers",
                data={
                    "session_id": session_id,
                    "page_id": "1",
                    "answers": '{"1": {"type": "essay", "value": "Memory test answer"}, "2": {"type": "slider", "value": 75}}'
                }
            )
            
            # Submit student info
            client.post("/examination/submit_student_info", data={
                "session_id": session_id,
                "name": f"Memory Test {i}",
                "email": f"memtest{i}@test.com",
                "phone": "555-0000",
                "age": "25",
                "education": "Bachelor's",
                "experience": "1-2 years"
            })
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f}MB, possible memory leak"


@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests using pytest-benchmark"""
    
    def test_homepage_benchmark(self, benchmark):
        """Benchmark homepage response time"""
        client = TestClient(app)
        
        def homepage_request():
            response = client.get("/")
            assert response.status_code == 200
            return response
        
        result = benchmark(homepage_request)
        
        # Benchmark should complete in reasonable time
        assert result.status_code == 200
    
    def test_database_query_benchmark(self, benchmark, populated_db):
        """Benchmark database query performance"""
        from app.services.question_service import get_questions_for_page
        from app.models.database import SessionLocal
        
        def query_questions():
            db = SessionLocal()
            try:
                questions = get_questions_for_page(db, page_id=1)
                return len(questions)
            finally:
                db.close()
        
        result = benchmark(query_questions)
        
        # Should return some questions
        assert result > 0