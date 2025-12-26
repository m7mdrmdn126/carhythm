#!/usr/bin/env python3
"""
Database Migration Script: Add Arabic Translation Columns
Run this script to add bilingual support to CaRhythm assessment system.

Usage:
    python scripts/add_translation_columns.py
"""

import sqlite3
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

DB_PATH = "career_dna.db"
BACKUP_SUFFIX = datetime.now().strftime("%Y%m%d_%H%M%S")


def create_backup(db_path):
    """Create backup of database before migration"""
    backup_path = f"{db_path}.backup_{BACKUP_SUFFIX}"
    import shutil
    shutil.copy2(db_path, backup_path)
    print(f"✅ Backup created: {backup_path}")
    return backup_path


def add_translation_columns(cursor):
    """Add Arabic translation columns to questions and pages tables"""
    
    print("\n📝 Adding Arabic columns to 'questions' table...")
    
    # Questions table - Arabic columns
    questions_columns = [
        ("question_text_ar", "TEXT"),
        ("slider_min_label_ar", "VARCHAR(100)"),
        ("slider_max_label_ar", "VARCHAR(100)"),
        ("mcq_options_ar", "TEXT"),
        ("ordering_options_ar", "TEXT"),
        ("scene_title_ar", "VARCHAR(200)"),
        ("scene_narrative_ar", "TEXT"),
    ]
    
    for col_name, col_type in questions_columns:
        try:
            cursor.execute(f"ALTER TABLE questions ADD COLUMN {col_name} {col_type};")
            print(f"   ✓ Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"   ⚠ Column already exists: {col_name}")
            else:
                raise
    
    print("\n📝 Adding Arabic columns to 'pages' table...")
    
    # Pages table - Arabic columns
    pages_columns = [
        ("title_ar", "VARCHAR(200)"),
        ("description_ar", "TEXT"),
        ("module_name_ar", "VARCHAR(100)"),
        ("module_description_ar", "TEXT"),
        ("completion_message_ar", "TEXT"),
    ]
    
    for col_name, col_type in pages_columns:
        try:
            cursor.execute(f"ALTER TABLE pages ADD COLUMN {col_name} {col_type};")
            print(f"   ✓ Added column: {col_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print(f"   ⚠ Column already exists: {col_name}")
            else:
                raise


def verify_migration(cursor):
    """Verify that all columns were added successfully"""
    print("\n🔍 Verifying migration...")
    
    # Check questions table
    cursor.execute("PRAGMA table_info(questions);")
    questions_cols = {row[1] for row in cursor.fetchall()}
    
    required_q_cols = {
        'question_text_ar', 'slider_min_label_ar', 'slider_max_label_ar',
        'mcq_options_ar', 'ordering_options_ar', 'scene_title_ar', 'scene_narrative_ar'
    }
    
    missing_q = required_q_cols - questions_cols
    if missing_q:
        print(f"   ❌ Missing columns in questions: {missing_q}")
        return False
    else:
        print(f"   ✅ All questions columns present ({len(required_q_cols)} columns)")
    
    # Check pages table
    cursor.execute("PRAGMA table_info(pages);")
    pages_cols = {row[1] for row in cursor.fetchall()}
    
    required_p_cols = {
        'title_ar', 'description_ar', 'module_name_ar', 
        'module_description_ar', 'completion_message_ar'
    }
    
    missing_p = required_p_cols - pages_cols
    if missing_p:
        print(f"   ❌ Missing columns in pages: {missing_p}")
        return False
    else:
        print(f"   ✅ All pages columns present ({len(required_p_cols)} columns)")
    
    return True


def show_statistics(cursor):
    """Show database statistics after migration"""
    print("\n📊 Database Statistics:")
    
    cursor.execute("SELECT COUNT(*) FROM pages;")
    pages_count = cursor.fetchone()[0]
    print(f"   Pages/Modules: {pages_count}")
    
    cursor.execute("SELECT COUNT(*) FROM questions;")
    questions_count = cursor.fetchone()[0]
    print(f"   Questions: {questions_count}")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Use admin panel to add Arabic translations")
    print(f"   2. Or prepare CSV with translations for bulk import")
    print(f"   3. Test language switching in frontend")


def main():
    """Main migration function"""
    print("=" * 60)
    print("🌍 BILINGUAL SUPPORT MIGRATION - Adding Arabic Columns")
    print("=" * 60)
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database not found at {DB_PATH}")
        print(f"   Current directory: {os.getcwd()}")
        sys.exit(1)
    
    try:
        # Create backup
        backup_path = create_backup(DB_PATH)
        
        # Connect to database
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Run migration
        add_translation_columns(cursor)
        
        # Commit changes
        conn.commit()
        print("\n✅ Migration committed successfully")
        
        # Verify migration
        if verify_migration(cursor):
            print("\n✅ Migration completed successfully!")
            show_statistics(cursor)
        else:
            print("\n❌ Migration verification failed")
            print(f"   You can restore from backup: {backup_path}")
            sys.exit(1)
        
        # Close connection
        conn.close()
        
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        print(f"   Restore from backup: {backup_path}")
        sys.exit(1)


if __name__ == "__main__":
    main()
