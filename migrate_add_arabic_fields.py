#!/usr/bin/env python3
"""
Migration script to add Arabic translation fields to question_pool table
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app.models.database import engine
from sqlalchemy import text

def migrate_add_arabic_fields():
    """Add Arabic translation columns to question_pool table."""
    print("🔄 Starting migration: Adding Arabic fields to question_pool table")
    print("=" * 70)
    
    with engine.connect() as conn:
        try:
            # Check if columns already exist
            result = conn.execute(text("PRAGMA table_info(question_pool)"))
            existing_columns = [row[1] for row in result]
            
            columns_to_add = [
                ('question_text_ar', 'TEXT'),
                ('slider_min_label_ar', 'VARCHAR(100)'),
                ('slider_max_label_ar', 'VARCHAR(100)'),
                ('mcq_options_ar', 'TEXT'),
                ('ordering_options_ar', 'TEXT')
            ]
            
            added_count = 0
            
            for column_name, column_type in columns_to_add:
                if column_name not in existing_columns:
                    print(f"➕ Adding column: {column_name} ({column_type})")
                    conn.execute(text(f"ALTER TABLE question_pool ADD COLUMN {column_name} {column_type}"))
                    conn.commit()
                    added_count += 1
                else:
                    print(f"✓ Column already exists: {column_name}")
            
            print("=" * 70)
            if added_count > 0:
                print(f"✅ Successfully added {added_count} Arabic field(s) to question_pool table")
            else:
                print("✅ All Arabic fields already exist - no migration needed")
            
            print("\n📊 Current question_pool table structure:")
            result = conn.execute(text("PRAGMA table_info(question_pool)"))
            for row in result:
                print(f"   - {row[1]} ({row[2]})")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Error during migration: {e}")
            conn.rollback()
            return False

if __name__ == "__main__":
    success = migrate_add_arabic_fields()
    sys.exit(0 if success else 1)
