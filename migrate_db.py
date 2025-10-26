"""
Database Migration Script for MCQ and Ordering Question Types
Adds new fields to existing tables while maintaining backwards compatibility
"""

import sqlite3
import os
import sys

# Add the app directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

def run_migration():
    """Run database migration to add new question type fields"""
    print("🔄 Starting database migration for MCQ and Ordering question types...")
    
    # Database path
    db_path = "career_assessment.db"
    
    if not os.path.exists(db_path):
        print("📊 Database not found. Creating tables with new schema...")
        # Import and create tables with new schema
        from app.models.database import create_tables
        create_tables()
        print("✅ Database created with updated schema!")
        return True
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("📊 Checking current database schema...")
        
        # Check if new columns already exist
        cursor.execute("PRAGMA table_info(questions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        migrations_needed = []
        
        # Check for MCQ fields
        if 'mcq_options' not in columns:
            migrations_needed.append("ALTER TABLE questions ADD COLUMN mcq_options TEXT")
        if 'mcq_correct_answers' not in columns:
            migrations_needed.append("ALTER TABLE questions ADD COLUMN mcq_correct_answers TEXT")
        if 'allow_multiple_selection' not in columns:
            migrations_needed.append("ALTER TABLE questions ADD COLUMN allow_multiple_selection BOOLEAN DEFAULT 0")
        
        # Check for ordering fields
        if 'ordering_options' not in columns:
            migrations_needed.append("ALTER TABLE questions ADD COLUMN ordering_options TEXT")
        if 'randomize_order' not in columns:
            migrations_needed.append("ALTER TABLE questions ADD COLUMN randomize_order BOOLEAN DEFAULT 1")
        
        # Check for answer_json field
        cursor.execute("PRAGMA table_info(question_answers)")
        answer_columns = [column[1] for column in cursor.fetchall()]
        
        if 'answer_json' not in answer_columns:
            migrations_needed.append("ALTER TABLE question_answers ADD COLUMN answer_json TEXT")
        
        if not migrations_needed:
            print("✅ Database is already up to date. No migration needed.")
            return True
        
        # Run migrations
        print(f"🔧 Running {len(migrations_needed)} database migrations...")
        
        for migration in migrations_needed:
            print(f"   Executing: {migration}")
            cursor.execute(migration)
        
        # Commit changes
        conn.commit()
        print("✅ Database migration completed successfully!")
        
        # Verify migrations
        print("🔍 Verifying migration...")
        cursor.execute("PRAGMA table_info(questions)")
        new_columns = [column[1] for column in cursor.fetchall()]
        
        required_fields = [
            'mcq_options', 'mcq_correct_answers', 'allow_multiple_selection',
            'ordering_options', 'randomize_order'
        ]
        
        for field in required_fields:
            if field in new_columns:
                print(f"   ✅ {field}")
            else:
                print(f"   ❌ {field} - MISSING")
                return False
        
        cursor.execute("PRAGMA table_info(question_answers)")
        answer_columns = [column[1] for column in cursor.fetchall()]
        
        if 'answer_json' in answer_columns:
            print(f"   ✅ answer_json")
        else:
            print(f"   ❌ answer_json - MISSING")
            return False
        
        print("🎉 Migration verification successful!")
        
        return True
        
    except sqlite3.Error as e:
        print(f"❌ Database error during migration: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during migration: {e}")
        return False
    finally:
        if conn:
            conn.close()

def backup_database():
    """Create a backup of the database before migration"""
    import shutil
    from datetime import datetime
    
    db_path = "career_assessment.db"
    if not os.path.exists(db_path):
        return True
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"career_assessment_backup_{timestamp}.db"
    
    try:
        shutil.copy2(db_path, backup_path)
        print(f"💾 Database backup created: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Failed to create database backup: {e}")
        return False

def main():
    """Main migration function"""
    print("🧬 Career DNA Assessment - Database Migration")
    print("=" * 60)
    
    # Create backup first
    if not backup_database():
        print("❌ Migration aborted due to backup failure")
        return
    
    # Run migration
    if run_migration():
        print("\n" + "=" * 60)
        print("🎉 Migration completed successfully!")
        print("📝 Summary of changes:")
        print("   - Added MCQ support with options and correct answers")
        print("   - Added ordering question support with randomization")
        print("   - Added JSON answer storage for complex question types")
        print("   - Maintained backwards compatibility with existing data")
        print("\n🚀 You can now use the new question types in the admin panel!")
    else:
        print("\n❌ Migration failed! Please check the error messages above.")
        print("💡 Your original database has been backed up for safety.")

if __name__ == "__main__":
    main()