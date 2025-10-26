#!/usr/bin/env python3
"""
Migration script to add Question Pool functionality
Creates new tables: categories, question_pool, question_page_assignments, import_logs
"""

import sqlite3
import os
from datetime import datetime

def migrate_question_pool():
    """Add question pool tables to the database."""
    db_path = "career_dna.db"
    
    if not os.path.exists(db_path):
        print("❌ Database file not found. Please ensure the main application has been run first.")
        return False
    
    # Create backup
    backup_path = f"career_dna_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
    print(f"📄 Creating backup: {backup_path}")
    
    try:
        with open(db_path, 'rb') as src, open(backup_path, 'wb') as dst:
            dst.write(src.read())
        print("✅ Backup created successfully")
    except Exception as e:
        print(f"❌ Failed to create backup: {e}")
        return False
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        print("🔄 Adding question pool tables...")
        
        # 1. Categories table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                description TEXT,
                color VARCHAR(7) DEFAULT '#3498db',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # 2. Question Pool table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_pool (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title VARCHAR(200) NOT NULL,
                question_text TEXT NOT NULL,
                question_type VARCHAR(20) NOT NULL,
                category_id INTEGER,
                
                -- Common fields
                is_required BOOLEAN DEFAULT 1,
                image_path VARCHAR(255),
                
                -- Essay fields
                essay_char_limit INTEGER,
                
                -- Slider fields
                slider_min_label VARCHAR(100),
                slider_max_label VARCHAR(100),
                
                -- MCQ fields
                mcq_options TEXT,
                mcq_correct_answer TEXT,
                allow_multiple_selection BOOLEAN DEFAULT 0,
                
                -- Ordering fields
                ordering_options TEXT,
                randomize_order BOOLEAN DEFAULT 1,
                
                -- Metadata
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(100),
                usage_count INTEGER DEFAULT 0,
                
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
        """)
        
        # 3. Question-Page assignments
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS question_page_assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question_pool_id INTEGER NOT NULL,
                page_id INTEGER NOT NULL,
                order_index INTEGER DEFAULT 0,
                assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                assigned_by VARCHAR(100),
                
                FOREIGN KEY (question_pool_id) REFERENCES question_pool(id) ON DELETE CASCADE,
                FOREIGN KEY (page_id) REFERENCES pages(id) ON DELETE CASCADE,
                UNIQUE(question_pool_id, page_id)
            )
        """)
        
        # 4. Import logs
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS import_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename VARCHAR(255) NOT NULL,
                import_type VARCHAR(50) NOT NULL,
                total_rows INTEGER DEFAULT 0,
                successful_imports INTEGER DEFAULT 0,
                failed_imports INTEGER DEFAULT 0,
                errors TEXT,
                imported_by VARCHAR(100),
                imported_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 5. Create indexes for better performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_question_pool_category ON question_pool(category_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_question_pool_type ON question_pool(question_type)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_page ON question_page_assignments(page_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_assignments_question ON question_page_assignments(question_pool_id)")
        
        # 6. Add default categories
        default_categories = [
            ("Personality Assessment", "Questions about personality traits and characteristics", "#e74c3c"),
            ("Skills Evaluation", "Questions about technical and soft skills", "#2ecc71"),
            ("Work Preferences", "Questions about work environment and preferences", "#3498db"),
            ("Career Goals", "Questions about career aspirations and goals", "#9b59b6"),
            ("General Assessment", "General assessment questions", "#34495e")
        ]
        
        for name, desc, color in default_categories:
            cursor.execute("""
                INSERT OR IGNORE INTO categories (name, description, color) 
                VALUES (?, ?, ?)
            """, (name, desc, color))
        
        conn.commit()
        print("✅ Question pool tables created successfully")
        
        # Verify tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'categories' OR name LIKE 'question_pool' OR name LIKE 'question_page_assignments' OR name LIKE 'import_logs'")
        tables = cursor.fetchall()
        print(f"✅ Verified {len(tables)} new tables created")
        
        # Show current data
        cursor.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        print(f"📊 Categories: {category_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
        return False
    
    finally:
        conn.close()

if __name__ == "__main__":
    print("🚀 Starting Question Pool Migration")
    print("=" * 50)
    
    success = migrate_question_pool()
    
    print("=" * 50)
    if success:
        print("🎉 Migration completed successfully!")
        print("📋 Next steps:")
        print("   1. Restart your application")
        print("   2. Access admin panel to manage question pool")
        print("   3. Download CSV templates for bulk import")
    else:
        print("💥 Migration failed!")
        print("🔄 Database has been preserved - check backup file")