"""
Simple test to trace Holland Code bug through actual database flow
"""

import sys
sys.path.append('/media/mohamedramadan/work/Carhythm/carhythm')

from app.models.database import SessionLocal
from app.services.scoring_service_v1_1 import calculate_riasec_v1_1
from app.models import StudentResponse, Question, QuestionAnswer, Page
import uuid

db = SessionLocal()

# Create a simple test response
session_id = str(uuid.uuid4())
response = StudentResponse(
    session_id=session_id,
    email='debug@test.com',
    full_name='Holland Debug Test',
    age_group='25-34',
    country='Test',
    origin_country='Test'
)
db.add(response)
db.commit()
db.refresh(response)

print(f"Created test response ID: {response.id}")
print()

# Get RIASEC page
riasec_page = db.query(Page).filter(Page.order_index == 1).first()
if not riasec_page:
    print("ERROR: No RIASEC page found!")
    db.close()
    exit(1)

# Find one slider question for each domain and create answers
domains = ['R', 'I', 'A', 'S', 'E', 'C']
target_scores = {
    'R': 4.5,  # Second highest
    'I': 4.8,  # Highest - should be first in Holland Code
    'A': 3.2,  # Third highest
    'S': 2.0,
    'E': 2.5,
    'C': 3.0
}

print("Creating answers with scores:")
for domain in domains:
    # Find a slider question for this domain
    question = db.query(Question).filter(
        Question.page_id == riasec_page.id,
        Question.domain == domain,
        Question.question_type == 'slider'
    ).first()
    
    if question:
        answer = QuestionAnswer(
            response_id=response.id,
            question_id=question.id,
            answer_value=target_scores[domain]
        )
        db.add(answer)
        print(f"  {domain}: {target_scores[domain]}")

db.commit()
print()

# Now calculate RIASEC - this should trigger debug output
print("=" * 60)
print("CALCULATING RIASEC...")
print("=" * 60)

result = calculate_riasec_v1_1(db, response.id)

print()
print("=" * 60)
print("RESULTS:")
print("=" * 60)
if result:
    print(f"Holland Code: {result['holland_code']}")
    print(f"Raw scores: {result['raw_scores']}")
    print()
    print("Sorted by score:")
    sorted_scores = sorted(result['raw_scores'].items(), key=lambda x: x[1], reverse=True)
    for domain, score in sorted_scores:
        print(f"  {domain}: {score}")
    print()
    expected = ''.join([d[0] for d in sorted_scores[:3]])
    print(f"Expected Holland Code: {expected}")
    print(f"Actual Holland Code:   {result['holland_code']}")
    
    if expected == result['holland_code']:
        print("\n✅ CORRECT!")
    else:
        print("\n❌ BUG CONFIRMED!")
else:
    print("ERROR: No result returned")

# Cleanup
db.delete(response)
db.commit()
db.close()
