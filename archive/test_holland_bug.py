"""
Test to generate a PDF with specific RIASEC scores to verify Holland Code bug.
Testing with scores: I (13.8) > R (12.5) > A (11.2)
Expected Holland Code: IRA
"""

import sys
sys.path.append('/media/mohamedramadan/work/Carhythm/carhythm')

from app.services.pdf_service import generate_pdf_report

# Mock data with problematic scores
response_data = {
    'student_name': 'Test Student',
    'email': 'test@example.com',
    'phone': '1234567890',
    'age_group': '18-24',
    'country': 'USA',
    'origin_country': 'USA'
}

scores_data = {
    'riasec_raw_scores': {
        'R': 12.5,
        'I': 13.8,  # Highest
        'A': 11.2,
        'S': 8.0,
        'E': 9.0,
        'C': 10.0
    },
    'riasec_strength_labels': {
        'R': 'High',
        'I': 'Very High',
        'A': 'High',
        'S': 'Medium',
        'E': 'Medium',
        'C': 'High'
    },
    'holland_code': 'RIA',  # WRONG - should be IRA
    'bigfive_raw_scores': {
        'O': 15.0,
        'C': 18.0,
        'E': 12.0,
        'A': 14.0,
        'N': 10.0
    },
    'bigfive_strength_labels': {
        'O': 'Medium',
        'C': 'High',
        'E': 'Medium',
        'A': 'Medium',
        'N': 'Low'
    },
    'behavioral_strength_labels': {},
    'behavioral_flags': {},
    'ikigai_zones': {},
    'behavioral_raw_scores': {}
}

# Generate PDF
print("Generating PDF with WRONG Holland Code: RIA")
print(f"Scores: I={scores_data['riasec_raw_scores']['I']}, R={scores_data['riasec_raw_scores']['R']}, A={scores_data['riasec_raw_scores']['A']}")
print()

pdf_buffer = generate_pdf_report(
    response_data,
    scores_data,
    is_free_version=False,  # Full version
    checkout_url='https://carhythm.com/paid',
    discount_code='LAUNCH50'
)

# Save to file
with open('/media/mohamedramadan/work/Carhythm/carhythm/test_holland_bug.pdf', 'wb') as f:
    f.write(pdf_buffer.getvalue())

print("✅ PDF generated: test_holland_bug.pdf")
print()
print("The PDF should show:")
print("  - Holland Code: RIA")
print("  - Top areas: R (12.5), I (13.8), A (11.2)")
print()
print("This demonstrates the bug: I has highest score but Holland Code starts with R")
