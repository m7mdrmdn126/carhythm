#!/usr/bin/env python3
"""
Create sample MCQ and ordering questions for testing
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models import get_db, Page, Question, QuestionType
from app.services import question_service
from app.schemas import PageCreate, QuestionCreate
import json

def create_sample_data():
    """Create sample pages and questions with new MCQ and ordering types."""
    db = next(get_db())
    
    try:
        # Get existing sample page
        existing_page = db.query(Page).filter(Page.title == "Sample Assessment").first()
        if existing_page:
            page = existing_page
            print(f"Using existing page: {page.title}")
        else:
            # Create a new page
            page_data = PageCreate(
                title="Sample Assessment",
                description="Sample questions to test MCQ and ordering functionality",
                order_index=99,
                is_active=True
            )
            page = question_service.create_page(db, page_data)
            print(f"Created page: {page.title}")
        
        # Check if MCQ questions already exist
        existing_questions = question_service.get_questions_by_page(db, page.id)
        mcq_questions = [q for q in existing_questions if q.question_type == QuestionType.mcq]
        if mcq_questions:
            print(f"MCQ questions already exist ({len(mcq_questions)} found)")
            return
        
        # Create MCQ question (single selection)
        mcq_single = QuestionCreate(
            page_id=page.id,
            question_text="What is your preferred work environment?",
            question_type=QuestionType.mcq,
            order_index=1,
            is_required=True,
            mcq_options=["Remote/Home office", "Traditional office", "Hybrid (mix of both)", "Co-working space"],
            mcq_correct_answer=[0],  # First option is "correct" for demo
            allow_multiple_selection=False
        )
        q1 = question_service.create_question(db, mcq_single)
        print(f"Created MCQ (single): {q1.question_text[:50]}...")
        
        # Create MCQ question (multiple selection)
        mcq_multi = QuestionCreate(
            page_id=page.id,
            question_text="Which skills are most important to you? (Select all that apply)",
            question_type=QuestionType.mcq,
            order_index=2,
            is_required=True,
            mcq_options=["Leadership", "Technical expertise", "Communication", "Creativity", "Problem-solving", "Teamwork"],
            mcq_correct_answer=[0, 2, 4],  # Multiple correct answers for demo
            allow_multiple_selection=True
        )
        q2 = question_service.create_question(db, mcq_multi)
        print(f"Created MCQ (multi): {q2.question_text[:50]}...")
        
        # Create ordering question
        ordering_q = QuestionCreate(
            page_id=page.id,
            question_text="Rank these career factors in order of importance to you (drag to reorder):",
            question_type=QuestionType.ordering,
            order_index=3,
            is_required=True,
            ordering_options=["High salary", "Work-life balance", "Job security", "Career growth", "Company culture", "Flexible schedule"],
            randomize_order=True
        )
        q3 = question_service.create_question(db, ordering_q)
        print(f"Created Ordering: {q3.question_text[:50]}...")
        
        # Create another MCQ with different options
        mcq_personality = QuestionCreate(
            page_id=page.id,
            question_text="Which personality trait best describes you?",
            question_type=QuestionType.mcq,
            order_index=4,
            is_required=True,
            mcq_options=["Introverted", "Extroverted", "Analytical", "Creative", "Detail-oriented", "Big-picture thinker"],
            mcq_correct_answer=[1],  # No real "correct" answer, just for demo
            allow_multiple_selection=False
        )
        q4 = question_service.create_question(db, mcq_personality)
        print(f"Created MCQ (personality): {q4.question_text[:50]}...")
        
        # Create ordering question for priorities
        ordering_priorities = QuestionCreate(
            page_id=page.id,
            question_text="Order these daily work activities by your preference (most preferred first):",
            question_type=QuestionType.ordering,
            order_index=5,
            is_required=True,
            ordering_options=["Strategic planning", "Hands-on execution", "Team meetings", "Individual work", "Problem-solving", "Learning new skills"],
            randomize_order=True
        )
        q5 = question_service.create_question(db, ordering_priorities)
        print(f"Created Ordering (priorities): {q5.question_text[:50]}...")
        
        print("\n✅ Sample data created successfully!")
        print("🌐 Visit http://localhost:8000/admin/login to manage questions")
        print("👤 Visit http://localhost:8000/student/welcome to take the assessment")
        print("🔑 Admin credentials: username=admin, password=admin123")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()