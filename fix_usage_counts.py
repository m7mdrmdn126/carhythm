#!/usr/bin/env python3
"""
Fix null usage_count values in question_pool table
"""

import sqlite3

def fix_usage_counts():
    """Fix null usage_count values in the database."""
    db_path = "career_dna.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Update null usage_count values to 0
        cursor.execute("""
            UPDATE question_pool 
            SET usage_count = 0 
            WHERE usage_count IS NULL
        """)
        
        updated_rows = cursor.rowcount
        conn.commit()
        
        print(f"✅ Fixed {updated_rows} null usage_count values")
        
        # Verify the fix
        cursor.execute("SELECT COUNT(*) FROM question_pool WHERE usage_count IS NULL")
        null_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM question_pool")
        total_count = cursor.fetchone()[0]
        
        print(f"📊 Database status:")
        print(f"   Total questions: {total_count}")
        print(f"   Null usage_count: {null_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error fixing usage counts: {e}")
        return False
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    print("🔧 Fixing null usage_count values...")
    print("=" * 40)
    
    success = fix_usage_counts()
    
    print("=" * 40)
    if success:
        print("🎉 Fix completed successfully!")
    else:
        print("💥 Fix failed!")