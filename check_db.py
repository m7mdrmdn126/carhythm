#!/usr/bin/env python3
"""Check database tables and data"""

from app.models.database import engine, SessionLocal
from app.models import Category, QuestionPool
from sqlalchemy import text

print("=" * 70)
print("DATABASE CHECK")
print("=" * 70)

# Check tables
with engine.connect() as conn:
    result = conn.execute(text("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"))
    tables = [row[0] for row in result]
    print(f"\n✓ Found {len(tables)} tables")

# Check categories
db = SessionLocal()
try:
    categories = db.query(Category).all()
    print(f"\n📁 Categories: {len(categories)}")
    if categories:
        for cat in categories:
            print(f"   - {cat.name} (ID: {cat.id})")
    else:
        print("   ⚠️  No categories found - creating default ones...")
        default_categories = [
            {"name": "Career Goals", "description": "Questions about career aspirations", "color": "#3498db"},
            {"name": "Skills Evaluation", "description": "Questions to assess skills", "color": "#2ecc71"},
            {"name": "Work Preferences", "description": "Questions about work style", "color": "#e74c3c"},
            {"name": "Personal Growth", "description": "Personal development questions", "color": "#f39c12"},
            {"name": "Personality Assessment", "description": "Personality-related questions", "color": "#9b59b6"}
        ]
        for cat_data in default_categories:
            cat = Category(**cat_data)
            db.add(cat)
        db.commit()
        print(f"   ✓ Created {len(default_categories)} default categories")
    
    # Check question pool
    questions = db.query(QuestionPool).all()
    print(f"\n❓ Question Pool: {len(questions)} questions")
    if questions:
        for q in questions[:5]:
            print(f"   - {q.title} ({q.question_type})")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
finally:
    db.close()

print("\n" + "=" * 70)
