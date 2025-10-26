#!/usr/bin/env python3
"""
Sample data script to populate the question pool with example questions
"""

import sqlite3
import json
from datetime import datetime

def populate_question_pool():
    """Add sample questions to the question pool."""
    
    # Connect to database
    conn = sqlite3.connect("career_dna.db")
    cursor = conn.cursor()
    
    try:
        print("🔄 Adding sample questions to question pool...")
        
        # Sample questions data
        sample_questions = [
            # Essay Questions
            {
                "title": "Career Goals Essay",
                "question_text": "Describe your long-term career goals and how you plan to achieve them. What specific steps will you take over the next 5 years?",
                "question_type": "essay",
                "category_id": 4,  # Career Goals category
                "essay_char_limit": 1000,
                "is_required": True,
                "created_by": "admin"
            },
            {
                "title": "Leadership Experience",
                "question_text": "Tell us about a time when you had to lead a team or project. What challenges did you face and how did you overcome them?",
                "question_type": "essay",
                "category_id": 2,  # Skills Evaluation category
                "essay_char_limit": 800,
                "is_required": True,
                "created_by": "admin"
            },
            
            # Slider Questions
            {
                "title": "Communication Skills Rating",
                "question_text": "Rate your communication skills on a scale from poor to excellent",
                "question_type": "slider",
                "category_id": 2,  # Skills Evaluation category
                "slider_min_label": "Poor",
                "slider_max_label": "Excellent",
                "is_required": True,
                "created_by": "admin"
            },
            {
                "title": "Team Collaboration Preference",
                "question_text": "How much do you enjoy working in team environments?",
                "question_type": "slider",
                "category_id": 3,  # Work Preferences category
                "slider_min_label": "Prefer Solo Work",
                "slider_max_label": "Love Team Work",
                "is_required": True,
                "created_by": "admin"
            },
            
            # MCQ Questions
            {
                "title": "Work Environment Preference",
                "question_text": "What is your preferred work environment?",
                "question_type": "mcq",
                "category_id": 3,  # Work Preferences category
                "mcq_options": json.dumps(["Remote/Home office", "Traditional office", "Hybrid (mix of both)", "Co-working space"]),
                "mcq_correct_answer": json.dumps([0]),  # No "correct" answer for preference
                "allow_multiple_selection": False,
                "is_required": True,
                "created_by": "admin"
            },
            {
                "title": "Important Skills Assessment",
                "question_text": "Which skills are most important to you? (Select all that apply)",
                "question_type": "mcq",
                "category_id": 2,  # Skills Evaluation category
                "mcq_options": json.dumps(["Leadership", "Technical expertise", "Communication", "Creativity", "Problem-solving", "Teamwork"]),
                "mcq_correct_answer": json.dumps([1, 2, 4]),  # Technical, Communication, Problem-solving
                "allow_multiple_selection": True,
                "is_required": True,
                "created_by": "admin"
            },
            
            # Ordering Questions
            {
                "title": "Career Priorities Ranking",
                "question_text": "Rank these career factors in order of importance to you (most important first)",
                "question_type": "ordering",
                "category_id": 4,  # Career Goals category
                "ordering_options": json.dumps(["High salary", "Work-life balance", "Job security", "Career growth", "Company culture", "Flexible schedule"]),
                "randomize_order": True,
                "is_required": True,
                "created_by": "admin"
            },
            {
                "title": "Daily Work Activities Preference",
                "question_text": "Order these daily work activities by your preference (most preferred first)",
                "question_type": "ordering",
                "category_id": 3,  # Work Preferences category
                "ordering_options": json.dumps(["Strategic planning", "Hands-on execution", "Team meetings", "Individual work", "Problem-solving", "Learning new skills"]),
                "randomize_order": False,
                "is_required": True,
                "created_by": "admin"
            }
        ]
        
        # Insert questions
        for question in sample_questions:
            cursor.execute("""
                INSERT INTO question_pool (
                    title, question_text, question_type, category_id, is_required,
                    essay_char_limit, slider_min_label, slider_max_label,
                    mcq_options, mcq_correct_answer, allow_multiple_selection,
                    ordering_options, randomize_order, created_by, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                question['title'],
                question['question_text'],
                question['question_type'],
                question['category_id'],
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
                datetime.now().isoformat()
            ))
        
        conn.commit()
        print(f"✅ Added {len(sample_questions)} sample questions to the pool")
        
        # Show statistics
        cursor.execute("SELECT question_type, COUNT(*) FROM question_pool GROUP BY question_type")
        stats = cursor.fetchall()
        print("\n📊 Question Pool Statistics:")
        for qtype, count in stats:
            print(f"   {qtype.title()}: {count}")
        
        cursor.execute("SELECT COUNT(*) FROM question_pool")
        total = cursor.fetchone()[0]
        print(f"   Total: {total}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error adding sample questions: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

def check_existing_data():
    """Check if sample data already exists."""
    conn = sqlite3.connect("career_dna.db")
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT COUNT(*) FROM question_pool WHERE created_by = 'admin'")
        count = cursor.fetchone()[0]
        return count > 0
    except:
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Question Pool Sample Data Script")
    print("=" * 50)
    
    if check_existing_data():
        print("ℹ️  Sample data already exists in the question pool")
        print("📊 Current data:")
        
        conn = sqlite3.connect("career_dna.db")
        cursor = conn.cursor()
        cursor.execute("SELECT question_type, COUNT(*) FROM question_pool GROUP BY question_type")
        stats = cursor.fetchall()
        for qtype, count in stats:
            print(f"   {qtype.title()}: {count}")
        cursor.execute("SELECT COUNT(*) FROM question_pool")
        total = cursor.fetchone()[0]
        print(f"   Total: {total}")
        conn.close()
    else:
        success = populate_question_pool()
        
        print("=" * 50)
        if success:
            print("🎉 Sample data added successfully!")
            print("📋 Next steps:")
            print("   1. Access the admin panel at http://localhost:8000/admin/login")
            print("   2. Go to 'Question Pool' to see the sample questions")
            print("   3. Go to 'Categories' to manage question categories")
            print("   4. Download CSV templates to add more questions in bulk")
        else:
            print("💥 Failed to add sample data!")