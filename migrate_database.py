"""
Database Migration Script for MCQ and Ordering Question Types
Adds new fields to existing Question and QuestionAnswer tables
"""

import sqlite3
import os
import sys
from datetime import datetime

# Database path
DB_PATH = "career_dna.db"

def backup_database():
    """Create a backup of the existing database"""
    backup_path = f"career_dna_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    
    if os.path.exists(DB_PATH):
        import shutil
        shutil.copy2(DB_PATH, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return backup_path
    else:
        print(f"❌ Database not found at: {DB_PATH}")
        return None

def check_existing_columns():
    """Check which new columns already exist"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check questions table
    cursor.execute("PRAGMA table_info(questions)")
    question_columns = [col[1] for col in cursor.fetchall()]
    
    # Check question_answers table
    cursor.execute("PRAGMA table_info(question_answers)")
    answer_columns = [col[1] for col in cursor.fetchall()]
    
    conn.close()
    
    return question_columns, answer_columns

def add_new_columns():
    """Add new columns to existing tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        question_columns, answer_columns = check_existing_columns()
        
        # Add new columns to questions table
        new_question_columns = [
            ("mcq_options", "TEXT"),
            ("mcq_correct_answer", "TEXT"),
            ("ordering_options", "TEXT"), 
            ("allow_multiple_selection", "BOOLEAN DEFAULT 0"),
            ("randomize_order", "BOOLEAN DEFAULT 0")
        ]
        
        for col_name, col_type in new_question_columns:
            if col_name not in question_columns:
                cursor.execute(f"ALTER TABLE questions ADD COLUMN {col_name} {col_type}")
                print(f"✅ Added column {col_name} to questions table")
            else:
                print(f"ℹ️  Column {col_name} already exists in questions table")
        
        # Add new column to question_answers table
        if "answer_json" not in answer_columns:
            cursor.execute("ALTER TABLE question_answers ADD COLUMN answer_json TEXT")
            print("✅ Added column answer_json to question_answers table")
        else:
            print("ℹ️  Column answer_json already exists in question_answers table")
        
        # Update QuestionType enum - SQLite doesn't support ALTER COLUMN, so we need to check enum values during runtime
        print("ℹ️  QuestionType enum will be updated in application code")
        
        conn.commit()
        print("✅ All database migrations completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ Migration failed: {e}")
        raise
    finally:
        conn.close()

def verify_migration():
    """Verify the migration was successful"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check questions table structure
        cursor.execute("PRAGMA table_info(questions)")
        question_columns = cursor.fetchall()
        
        # Check question_answers table structure  
        cursor.execute("PRAGMA table_info(question_answers)")
        answer_columns = cursor.fetchall()
        
        print("\n📋 Updated Questions Table Structure:")
        for col in question_columns:
            print(f"  - {col[1]}: {col[2]}")
        
        print("\n📋 Updated Question_Answers Table Structure:")
        for col in answer_columns:
            print(f"  - {col[1]}: {col[2]}")
        
        # Test a simple query
        cursor.execute("SELECT COUNT(*) FROM questions")
        question_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM question_answers") 
        answer_count = cursor.fetchone()[0]
        
        print(f"\n📊 Current Data:")
        print(f"  - Questions: {question_count}")
        print(f"  - Answers: {answer_count}")
        
    except Exception as e:
        print(f"❌ Verification failed: {e}")
    finally:
        conn.close()

def main():
    """Main migration function"""
    print("🧬 Career DNA Assessment - Database Migration")
    print("=" * 50)
    print("Adding support for MCQ and Ordering question types")
    print()
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found: {DB_PATH}")
        print("Make sure you're in the correct directory")
        return False
    
    print(f"📂 Found database: {DB_PATH}")
    
    # Create backup
    backup_path = backup_database()
    if not backup_path:
        return False
    
    try:
        # Perform migration
        add_new_columns()
        
        # Verify migration
        verify_migration()
        
        print(f"\n🎉 Migration completed successfully!")
        print(f"📁 Backup saved as: {backup_path}")
        print("\nYou can now use the new MCQ and Ordering question types!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"💾 Database backup is available at: {backup_path}")
        print("You can restore it if needed.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)