"""
Database Migration Script for Story Mode Enhancement
Adds new fields to questions and pages tables for Story Mode functionality.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.models.database import engine
from sqlalchemy import text

def migrate_database():
    """Add Story Mode fields to existing tables."""
    print("🔄 Starting Story Mode database migration...")
    
    with engine.connect() as conn:
        try:
            # Add fields to questions table
            print("📝 Adding Story Mode fields to questions table...")
            
            # Check if columns already exist before adding
            result = conn.execute(text("PRAGMA table_info(questions)"))
            existing_columns = {row[1] for row in result}
            
            if 'scene_title' not in existing_columns:
                conn.execute(text("ALTER TABLE questions ADD COLUMN scene_title VARCHAR(200)"))
                print("  ✅ Added scene_title")
            
            if 'scene_narrative' not in existing_columns:
                conn.execute(text("ALTER TABLE questions ADD COLUMN scene_narrative TEXT"))
                print("  ✅ Added scene_narrative")
            
            if 'scene_image_url' not in existing_columns:
                conn.execute(text("ALTER TABLE questions ADD COLUMN scene_image_url VARCHAR(500)"))
                print("  ✅ Added scene_image_url")
            
            if 'scene_theme' not in existing_columns:
                conn.execute(text("ALTER TABLE questions ADD COLUMN scene_theme VARCHAR(50)"))
                print("  ✅ Added scene_theme")
            
            # Add fields to pages table
            print("📄 Adding module organization fields to pages table...")
            
            result = conn.execute(text("PRAGMA table_info(pages)"))
            existing_columns = {row[1] for row in result}
            
            if 'module_name' not in existing_columns:
                conn.execute(text("ALTER TABLE pages ADD COLUMN module_name VARCHAR(100)"))
                print("  ✅ Added module_name")
            
            if 'module_emoji' not in existing_columns:
                conn.execute(text("ALTER TABLE pages ADD COLUMN module_emoji VARCHAR(10)"))
                print("  ✅ Added module_emoji")
            
            if 'chapter_number' not in existing_columns:
                conn.execute(text("ALTER TABLE pages ADD COLUMN chapter_number INTEGER"))
                print("  ✅ Added chapter_number")
            
            if 'estimated_minutes' not in existing_columns:
                conn.execute(text("ALTER TABLE pages ADD COLUMN estimated_minutes INTEGER"))
                print("  ✅ Added estimated_minutes")
            
            if 'completion_message' not in existing_columns:
                conn.execute(text("ALTER TABLE pages ADD COLUMN completion_message TEXT"))
                print("  ✅ Added completion_message")
            
            conn.commit()
            
            print("\n✅ Migration completed successfully!")
            print("\n📊 Story Mode fields are now available in the database.")
            print("   Admins can now add scene narratives, titles, and module organization.")
            
        except Exception as e:
            print(f"\n❌ Migration failed: {e}")
            conn.rollback()
            sys.exit(1)

if __name__ == "__main__":
    migrate_database()
