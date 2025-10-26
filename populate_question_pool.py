#!/usr/bin/env python3
"""
Script to populate the question pool with sample questions for testing
"""

import sqlite3
import json
from datetime import datetime

def populate_question_pool():
    """Add sample questions to the question pool."""
    db_path = "career_dna.db"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 Adding sample questions to question pool...")
        
        # Sample questions data
        sample_questions = [
            # Essay questions
            {
                "title": "Career Goals Description",
                "question_text": "Describe your short-term and long-term career goals. What steps are you taking to achieve them?",
                "question_type": "essay",
                "category_id": 4,  # Career Goals
                "is_required": True,
                "essay_char_limit": 1000,
                "created_by": "system"
            },
            {
                "title": "Greatest Professional Achievement",
                "question_text": "Tell us about your greatest professional achievement and what you learned from it.",
                "question_type": "essay", 
                "category_id": 2,  # Skills Evaluation
                "is_required": True,
                "essay_char_limit": 800,
                "created_by": "system"
            },
            
            # Slider questions
            {
                "title": "Leadership Preference",
                "question_text": "How much do you prefer taking leadership roles?",
                "question_type": "slider",
                "category_id": 2,  # Skills Evaluation
                "is_required": True,
                "slider_min_label": "Prefer to Follow",
                "slider_max_label": "Natural Leader",
                "created_by": "system"
            },
            {
                "title": "Risk Tolerance Level",
                "question_text": "How comfortable are you with taking calculated risks?",
                "question_type": "slider",
                "category_id": 1,  # Personality Assessment
                "is_required": True,
                "slider_min_label": "Risk Averse",
                "slider_max_label": "Risk Taker",
                "created_by": "system"
            },
            
            # MCQ questions
            {
                "title": "Preferred Work Environment",
                "question_text": "What type of work environment do you prefer?",
                "question_type": "mcq",
                "category_id": 3,  # Work Preferences
                "is_required": True,
                "mcq_options": json.dumps(["Remote/Home office", "Traditional office", "Hybrid (mix of both)", "Co-working space", "Outdoor/Field work"]),
                "mcq_correct_answer": json.dumps([0]),  # No "correct" answer for preference
                "allow_multiple_selection": False,
                "created_by": "system"
            },
            {
                "title": "Important Skills (Multi-select)",
                "question_text": "Which skills are most important to you? (Select all that apply)",
                "question_type": "mcq",
                "category_id": 2,  # Skills Evaluation
                "is_required": True,
                "mcq_options": json.dumps(["Leadership", "Technical expertise", "Communication", "Creativity", "Problem-solving", "Teamwork"]),
                "mcq_correct_answer": json.dumps([0, 1, 2, 3, 4, 5]),  # All are valid
                "allow_multiple_selection": True,
                "created_by": "system"
            },
            
            # Ordering questions
            {
                "title": "Career Factors Priority",
                "question_text": "Rank these career factors in order of importance to you (most important first):",
                "question_type": "ordering",
                "category_id": 3,  # Work Preferences
                "is_required": True,
                "ordering_options": json.dumps(["High salary", "Work-life balance", "Job security", "Career growth", "Company culture", "Flexible schedule"]),
                "randomize_order": True,
                "created_by": "system"
            },
            {
                "title": "Daily Activities Preference",
                "question_text": "Order these daily work activities by your preference (most preferred first):",
                "question_type": "ordering",
                "category_id": 3,  # Work Preferences
                "is_required": True,
                "ordering_options": json.dumps(["Strategic planning", "Hands-on execution", "Team meetings", "Individual work", "Problem-solving", "Learning new skills"]),
                "randomize_order": False,
                "created_by": "system"
            }
        ]
        
        # Insert questions
        for i, question in enumerate(sample_questions, 1):
            cursor.execute("""
                INSERT OR IGNORE INTO question_pool 
                (title, question_text, question_type, category_id, is_required, 
                 essay_char_limit, slider_min_label, slider_max_label, 
                 mcq_options, mcq_correct_answer, allow_multiple_selection,
                 ordering_options, randomize_order, created_by, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                question['title'],
                question['question_text'], 
                question['question_type'],
                question.get('category_id'),
                question['is_required'],
                question.get('essay_char_limit'),
                question.get('slider_min_label'),
                question.get('slider_max_label'),
                question.get('mcq_options'),
                question.get('mcq_correct_answer'),
                question.get('allow_multiple_selection', False),
                question.get('ordering_options'),
                question.get('randomize_order', True),
                question['created_by'],
                datetime.now()
            ))
        
        conn.commit()
        
        # Check what was inserted
        cursor.execute("SELECT COUNT(*) FROM question_pool")
        pool_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        
        print(f"✅ Sample questions added successfully")
        print(f"📊 Question Pool: {pool_count} questions")
        print(f"📊 Categories: {category_count} categories")
        
        # Show some stats
        cursor.execute("""
            SELECT question_type, COUNT(*) 
            FROM question_pool 
            GROUP BY question_type
        """)
        
        type_stats = cursor.fetchall()
        print(f"📈 Questions by type:")
        for q_type, count in type_stats:
            print(f"   {q_type}: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to populate question pool: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Populating Question Pool with Sample Data")
    print("=" * 50)
    
    success = populate_question_pool()
    
    print("=" * 50)
    if success:
        print("🎉 Sample data added successfully!")
        print("📋 Next steps:")
        print("   1. Access /admin/question-pool to see the questions")
        print("   2. Try assigning questions to pages")
        print("   3. Test CSV import/export functionality")
    else:
        print("💥 Failed to add sample data!")