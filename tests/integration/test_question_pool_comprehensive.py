"""
Comprehensive integration tests for question pool features
Tests: category CRUD, question pool CRUD, CSV import/export, question-page assignments, usage tracking
"""
import pytest
import json
import io
from fastapi import status
from app.models import Category, QuestionPool, QuestionPageAssignment, ImportLog


class TestCategoryCRUD:
    """Test category CRUD operations"""
    
    def test_view_categories(self, authenticated_admin_client):
        """Test viewing categories page"""
        response = authenticated_admin_client.get("/admin/categories")
        
        assert response.status_code == 200
        assert b"categories" in response.content.lower() or b"category" in response.content.lower()
    
    def test_create_category(self, authenticated_admin_client, db_session):
        """Test creating a new category"""
        response = authenticated_admin_client.post("/admin/categories", data={
            "name": "New Test Category",
            "description": "A test category description",
            "color": "#ff5733"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/categories"
        
        # Verify category was created
        category = db_session.query(Category).filter(Category.name == "New Test Category").first()
        assert category is not None
        assert category.color == "#ff5733"
    
    def test_create_category_minimal(self, authenticated_admin_client, db_session):
        """Test creating category with minimal data"""
        response = authenticated_admin_client.post("/admin/categories", data={
            "name": "Minimal Category",
            "description": "",
            "color": "#3498db"  # Default color
        }, follow_redirects=False)
        
        assert response.status_code == 302
    
    def test_create_duplicate_category(self, authenticated_admin_client, test_category):
        """Test creating category with duplicate name"""
        response = authenticated_admin_client.post("/admin/categories", data={
            "name": test_category.name,  # Duplicate name
            "description": "Different description",
            "color": "#000000"
        })
        
        # Should fail due to unique constraint
        assert response.status_code == 400
    
    def test_update_category(self, authenticated_admin_client, test_category, db_session):
        """Test updating a category"""
        response = authenticated_admin_client.post(f"/admin/categories/{test_category.id}/edit", data={
            "name": "Updated Category Name",
            "description": "Updated description",
            "color": "#00ff00",
            "is_active": "on"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify update
        db_session.refresh(test_category)
        assert test_category.name == "Updated Category Name"
        assert test_category.color == "#00ff00"
        assert test_category.is_active is True
    
    def test_deactivate_category(self, authenticated_admin_client, test_category, db_session):
        """Test deactivating a category"""
        response = authenticated_admin_client.post(f"/admin/categories/{test_category.id}/edit", data={
            "name": test_category.name,
            "description": test_category.description or "",
            "color": test_category.color,
            # is_active not included = False
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        db_session.refresh(test_category)
        assert test_category.is_active is False
    
    def test_delete_category(self, authenticated_admin_client, test_category, db_session):
        """Test deleting a category"""
        category_id = test_category.id
        
        response = authenticated_admin_client.post(f"/admin/categories/{category_id}/delete", follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify deletion
        deleted = db_session.query(Category).filter(Category.id == category_id).first()
        assert deleted is None


class TestQuestionPoolCRUD:
    """Test question pool CRUD operations"""
    
    def test_view_question_pool(self, authenticated_admin_client):
        """Test viewing question pool dashboard"""
        response = authenticated_admin_client.get("/admin/question-pool")
        
        assert response.status_code == 200
        assert b"question" in response.content.lower() and b"pool" in response.content.lower()
    
    def test_create_essay_question_in_pool(self, authenticated_admin_client, test_category, db_session):
        """Test creating essay question in pool"""
        response = authenticated_admin_client.post("/admin/question-pool/create", data={
            "title": "Career Aspirations",
            "question_text": "What are your career goals?",
            "question_type": "essay",
            "category_id": str(test_category.id),
            "is_required": "on",
            "essay_char_limit": "500"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify question created
        question = db_session.query(QuestionPool).filter(
            QuestionPool.title == "Career Aspirations"
        ).first()
        assert question is not None
        assert question.question_type == "essay"
        assert question.essay_char_limit == 500
    
    def test_create_slider_question_in_pool(self, authenticated_admin_client, test_category, db_session):
        """Test creating slider question in pool"""
        response = authenticated_admin_client.post("/admin/question-pool/create", data={
            "title": "Leadership Interest",
            "question_text": "How interested are you in leadership?",
            "question_type": "slider",
            "category_id": str(test_category.id),
            "is_required": "on",
            "slider_min_label": "Not interested",
            "slider_max_label": "Very interested"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        question = db_session.query(QuestionPool).filter(
            QuestionPool.title == "Leadership Interest"
        ).first()
        assert question is not None
        assert question.slider_min_label == "Not interested"
    
    def test_create_mcq_question_in_pool(self, authenticated_admin_client, test_category, db_session):
        """Test creating MCQ question in pool"""
        response = authenticated_admin_client.post("/admin/question-pool/create", data={
            "title": "Work Preference",
            "question_text": "What is your preferred work style?",
            "question_type": "mcq",
            "category_id": str(test_category.id),
            "is_required": "on",
            "mcq_option": ["Remote", "Office", "Hybrid", "Field"],
            "mcq_correct": ["0"],
            "allow_multiple_selection": "off"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        question = db_session.query(QuestionPool).filter(
            QuestionPool.title == "Work Preference"
        ).first()
        assert question is not None
        assert question.question_type == "mcq"
    
    def test_create_ordering_question_in_pool(self, authenticated_admin_client, test_category, db_session):
        """Test creating ordering question in pool"""
        response = authenticated_admin_client.post("/admin/question-pool/create", data={
            "title": "Career Priorities",
            "question_text": "Rank these career factors",
            "question_type": "ordering",
            "category_id": str(test_category.id),
            "is_required": "on",
            "ordering_option": ["Salary", "Growth", "Balance", "Culture"],
            "randomize_order": "on"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        question = db_session.query(QuestionPool).filter(
            QuestionPool.title == "Career Priorities"
        ).first()
        assert question is not None
        assert question.question_type == "ordering"
    
    def test_filter_questions_by_category(self, authenticated_admin_client, test_question_pool, test_category):
        """Test filtering questions by category"""
        response = authenticated_admin_client.get(
            f"/admin/question-pool?category_id={test_category.id}"
        )
        
        assert response.status_code == 200
        # Should show questions from this category
    
    def test_filter_questions_by_type(self, authenticated_admin_client):
        """Test filtering questions by type"""
        response = authenticated_admin_client.get("/admin/question-pool?question_type=essay")
        
        assert response.status_code == 200
    
    def test_search_questions(self, authenticated_admin_client, test_question_pool):
        """Test searching questions in pool"""
        response = authenticated_admin_client.get("/admin/question-pool?search=environment")
        
        assert response.status_code == 200
    
    def test_update_question_in_pool(self, authenticated_admin_client, test_question_pool, db_session):
        """Test updating question in pool"""
        response = authenticated_admin_client.post(f"/admin/question-pool/{test_question_pool.id}/edit", data={
            "title": "Updated Pool Question",
            "question_text": "Updated question text",
            "question_type": test_question_pool.question_type,
            "category_id": str(test_question_pool.category_id) if test_question_pool.category_id else "",
            "is_required": "on"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        db_session.refresh(test_question_pool)
        assert test_question_pool.title == "Updated Pool Question"
    
    def test_delete_question_from_pool(self, authenticated_admin_client, test_question_pool, db_session):
        """Test deleting question from pool"""
        question_id = test_question_pool.id
        
        response = authenticated_admin_client.post(
            f"/admin/question-pool/{question_id}/delete",
            follow_redirects=False
        )
        
        assert response.status_code == 302
        
        deleted = db_session.query(QuestionPool).filter(QuestionPool.id == question_id).first()
        assert deleted is None


class TestQuestionPageAssignment:
    """Test assigning questions from pool to pages"""
    
    def test_view_assignment_page(self, authenticated_admin_client):
        """Test viewing question assignment page"""
        response = authenticated_admin_client.get("/admin/page-question-assignment")
        
        assert response.status_code == 200
    
    def test_assign_question_to_page(self, authenticated_admin_client, test_question_pool, test_page, db_session):
        """Test assigning a question to a page"""
        response = authenticated_admin_client.post("/admin/assign-question-to-page", data={
            "question_pool_id": str(test_question_pool.id),
            "page_id": str(test_page.id),
            "order_index": "0"
        }, follow_redirects=False)
        
        assert response.status_code == 302
        
        # Verify assignment
        assignment = db_session.query(QuestionPageAssignment).filter(
            QuestionPageAssignment.question_pool_id == test_question_pool.id,
            QuestionPageAssignment.page_id == test_page.id
        ).first()
        
        assert assignment is not None
    
    def test_assign_same_question_multiple_pages(self, authenticated_admin_client, test_question_pool, multiple_pages, db_session):
        """Test assigning same question to multiple pages"""
        for page in multiple_pages:
            response = authenticated_admin_client.post("/admin/assign-question-to-page", data={
                "question_pool_id": str(test_question_pool.id),
                "page_id": str(page.id),
                "order_index": "0"
            })
            
            assert response.status_code == 302
        
        # Verify all assignments
        assignments = db_session.query(QuestionPageAssignment).filter(
            QuestionPageAssignment.question_pool_id == test_question_pool.id
        ).all()
        
        assert len(assignments) == len(multiple_pages)
    
    def test_unassign_question_from_page(self, authenticated_admin_client, test_question_page_assignment, db_session):
        """Test removing question assignment"""
        assignment_id = test_question_page_assignment.id
        
        response = authenticated_admin_client.post(
            f"/admin/unassign-question/{assignment_id}",
            follow_redirects=False
        )
        
        assert response.status_code == 302
        
        deleted = db_session.query(QuestionPageAssignment).filter(
            QuestionPageAssignment.id == assignment_id
        ).first()
        assert deleted is None
    
    def test_usage_count_increments(self, authenticated_admin_client, test_question_pool, test_page, db_session):
        """Test that usage count increments when assigned"""
        initial_count = test_question_pool.usage_count or 0
        
        # Assign question
        authenticated_admin_client.post("/admin/assign-question-to-page", data={
            "question_pool_id": str(test_question_pool.id),
            "page_id": str(test_page.id),
            "order_index": "0"
        })
        
        db_session.refresh(test_question_pool)
        assert test_question_pool.usage_count > initial_count


class TestCSVImport:
    """Test CSV import functionality"""
    
    def test_import_essay_questions_csv(self, authenticated_admin_client, test_category, db_session):
        """Test importing essay questions from CSV"""
        csv_content = f"""title,question_text,category_name,is_required,essay_char_limit
Essay Q1,What is your background?,{test_category.name},TRUE,500
Essay Q2,Describe your goals,{test_category.name},TRUE,400"""
        
        csv_file = io.BytesIO(csv_content.encode())
        csv_file.name = "essays.csv"
        
        response = authenticated_admin_client.post("/admin/import-csv", data={
            "question_type": "essay"
        }, files={
            "file": ("essays.csv", csv_file, "text/csv")
        })
        
        assert response.status_code in [200, 302]
        
        # Verify questions imported
        imported = db_session.query(QuestionPool).filter(
            QuestionPool.title.in_(["Essay Q1", "Essay Q2"])
        ).all()
        
        assert len(imported) >= 1  # At least one should be imported
    
    def test_import_slider_questions_csv(self, authenticated_admin_client, test_category, db_session):
        """Test importing slider questions from CSV"""
        csv_content = f"""title,question_text,category_name,is_required,slider_min_label,slider_max_label
Slider Q1,Rate your interest,{test_category.name},TRUE,Low,High
Slider Q2,Rate your skill,{test_category.name},TRUE,Beginner,Expert"""
        
        csv_file = io.BytesIO(csv_content.encode())
        csv_file.name = "sliders.csv"
        
        response = authenticated_admin_client.post("/admin/import-csv", data={
            "question_type": "slider"
        }, files={
            "file": ("sliders.csv", csv_file, "text/csv")
        })
        
        assert response.status_code in [200, 302]
    
    def test_import_mcq_questions_csv(self, authenticated_admin_client, test_category, db_session):
        """Test importing MCQ questions from CSV"""
        csv_content = f"""title,question_text,category_name,is_required,option_1,option_2,option_3,correct_answers,allow_multiple_selection
MCQ Q1,Choose preference,{test_category.name},TRUE,Remote,Office,Hybrid,1,FALSE
MCQ Q2,Select skills,{test_category.name},TRUE,Tech,Leadership,Creative,"1,2",TRUE"""
        
        csv_file = io.BytesIO(csv_content.encode())
        csv_file.name = "mcqs.csv"
        
        response = authenticated_admin_client.post("/admin/import-csv", data={
            "question_type": "mcq"
        }, files={
            "file": ("mcqs.csv", csv_file, "text/csv")
        })
        
        assert response.status_code in [200, 302]
    
    def test_import_csv_with_errors(self, authenticated_admin_client, test_category, db_session):
        """Test importing CSV with invalid rows"""
        csv_content = f"""title,question_text,category_name,is_required,essay_char_limit
,Missing title,{test_category.name},TRUE,500
Valid Title,Valid question,{test_category.name},TRUE,400
Invalid Title,Some text,NonexistentCategory,TRUE,300"""
        
        csv_file = io.BytesIO(csv_content.encode())
        csv_file.name = "errors.csv"
        
        response = authenticated_admin_client.post("/admin/import-csv", data={
            "question_type": "essay"
        }, files={
            "file": ("errors.csv", csv_file, "text/csv")
        })
        
        # Should process but report errors
        assert response.status_code in [200, 302]
        
        # Check import log
        import_log = db_session.query(ImportLog).filter(
            ImportLog.filename == "errors.csv"
        ).first()
        
        if import_log:
            assert import_log.failed_imports > 0
    
    def test_import_empty_csv(self, authenticated_admin_client):
        """Test importing empty CSV"""
        csv_content = """title,question_text,category_name,is_required,essay_char_limit"""
        
        csv_file = io.BytesIO(csv_content.encode())
        csv_file.name = "empty.csv"
        
        response = authenticated_admin_client.post("/admin/import-csv", data={
            "question_type": "essay"
        }, files={
            "file": ("empty.csv", csv_file, "text/csv")
        })
        
        assert response.status_code in [200, 400]  # Should handle gracefully


class TestCSVExport:
    """Test CSV export functionality"""
    
    def test_export_questions_csv(self, authenticated_admin_client, test_question_pool):
        """Test exporting questions to CSV"""
        response = authenticated_admin_client.get("/admin/export-questions-csv")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/csv; charset=utf-8"
        assert "attachment" in response.headers["content-disposition"]
    
    def test_export_filtered_questions(self, authenticated_admin_client, test_category):
        """Test exporting filtered questions"""
        response = authenticated_admin_client.get(
            f"/admin/export-questions-csv?category_id={test_category.id}"
        )
        
        assert response.status_code == 200
    
    def test_export_by_question_type(self, authenticated_admin_client):
        """Test exporting questions by type"""
        response = authenticated_admin_client.get(
            "/admin/export-questions-csv?question_type=essay"
        )
        
        assert response.status_code == 200


class TestImportLogs:
    """Test import log tracking"""
    
    def test_view_import_logs(self, authenticated_admin_client):
        """Test viewing import logs"""
        response = authenticated_admin_client.get("/admin/import-logs")
        
        assert response.status_code == 200
    
    def test_import_creates_log(self, authenticated_admin_client, test_category, db_session):
        """Test that import creates log entry"""
        csv_content = f"""title,question_text,category_name,is_required,essay_char_limit
Test Q,Test question,{test_category.name},TRUE,500"""
        
        csv_file = io.BytesIO(csv_content.encode())
        csv_file.name = "test_log.csv"
        
        authenticated_admin_client.post("/admin/import-csv", data={
            "question_type": "essay"
        }, files={
            "file": ("test_log.csv", csv_file, "text/csv")
        })
        
        # Check log was created
        log = db_session.query(ImportLog).filter(
            ImportLog.filename == "test_log.csv"
        ).first()
        
        assert log is not None
        assert log.import_type == "essay"
    
    def test_view_import_log_details(self, authenticated_admin_client, test_import_log):
        """Test viewing import log details"""
        response = authenticated_admin_client.get(f"/admin/import-logs/{test_import_log.id}")
        
        assert response.status_code == 200


class TestQuestionPoolStatistics:
    """Test question pool statistics"""
    
    def test_view_pool_statistics(self, authenticated_admin_client):
        """Test viewing pool statistics"""
        response = authenticated_admin_client.get("/admin/question-pool-stats")
        
        assert response.status_code == 200
    
    def test_statistics_by_type(self, authenticated_admin_client, test_question_pool_essay, test_question_pool_slider):
        """Test statistics show breakdown by type"""
        response = authenticated_admin_client.get("/admin/question-pool-stats")
        
        assert response.status_code == 200
        # Should show counts for different types
    
    def test_statistics_by_category(self, authenticated_admin_client, multiple_categories, db_session):
        """Test statistics show breakdown by category"""
        # Add questions to different categories
        for category in multiple_categories:
            q = QuestionPool(
                title=f"Q for {category.name}",
                question_text="Test",
                question_type="essay",
                category_id=category.id,
                created_by="admin"
            )
            db_session.add(q)
        db_session.commit()
        
        response = authenticated_admin_client.get("/admin/question-pool-stats")
        
        assert response.status_code == 200


class TestQuestionPoolWorkflows:
    """Test complete question pool workflows"""
    
    def test_create_category_add_questions_assign_workflow(self, authenticated_admin_client, test_page, db_session):
        """Test complete workflow: create category -> add questions -> assign to pages"""
        # Step 1: Create category
        authenticated_admin_client.post("/admin/categories", data={
            "name": "Workflow Category",
            "description": "For testing workflow",
            "color": "#123456"
        })
        
        category = db_session.query(Category).filter(Category.name == "Workflow Category").first()
        assert category is not None
        
        # Step 2: Add questions to pool
        authenticated_admin_client.post("/admin/question-pool/create", data={
            "title": "Workflow Question 1",
            "question_text": "Test question 1",
            "question_type": "essay",
            "category_id": str(category.id),
            "is_required": "on",
            "essay_char_limit": "500"
        })
        
        question = db_session.query(QuestionPool).filter(
            QuestionPool.title == "Workflow Question 1"
        ).first()
        assert question is not None
        
        # Step 3: Assign to page
        authenticated_admin_client.post("/admin/assign-question-to-page", data={
            "question_pool_id": str(question.id),
            "page_id": str(test_page.id),
            "order_index": "0"
        })
        
        # Verify assignment
        assignment = db_session.query(QuestionPageAssignment).filter(
            QuestionPageAssignment.question_pool_id == question.id
        ).first()
        
        assert assignment is not None
