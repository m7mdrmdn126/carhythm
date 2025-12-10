#!/bin/bash

# CaRhythm v1.1 Integration Test Script
# Tests end-to-end functionality of the new assessment system

echo "=================================="
echo "🧪 CaRhythm v1.1 Integration Tests"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# Function to print test results
test_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✓ PASSED${NC}: $2"
        ((PASSED++))
    else
        echo -e "${RED}✗ FAILED${NC}: $2"
        ((FAILED++))
    fi
}

echo "📋 Phase 1: Database Schema Validation"
echo "--------------------------------------"

# Test 1: Check if database exists
if [ -f "career_dna.db" ]; then
    test_result 0 "Database file exists"
else
    test_result 1 "Database file not found"
fi

# Test 2: Check if v1.1 tables have correct structure
python3 << 'EOF'
import sqlite3
import sys

try:
    conn = sqlite3.connect('career_dna.db')
    cursor = conn.cursor()
    
    # Check Question table for v1.1 fields
    cursor.execute("PRAGMA table_info(questions)")
    columns = [col[1] for col in cursor.fetchall()]
    
    required_fields = ['item_id', 'domain', 'tags', 'reverse_scored', 'scale_type', 'scale_labels']
    missing = [f for f in required_fields if f not in columns]
    
    if missing:
        print(f"Missing fields in questions table: {missing}", file=sys.stderr)
        sys.exit(1)
    
    # Check AssessmentScore table for v1.1 fields
    cursor.execute("PRAGMA table_info(assessment_scores)")
    columns = [col[1] for col in cursor.fetchall()]
    
    required_fields = ['riasec_raw_scores', 'riasec_strength_labels', 'behavioral_flags', 'ikigai_zones', 'rhythm_profile']
    missing = [f for f in required_fields if f not in columns]
    
    if missing:
        print(f"Missing fields in assessment_scores table: {missing}", file=sys.stderr)
        sys.exit(1)
    
    conn.close()
    sys.exit(0)
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

test_result $? "Database schema has v1.1 fields"

echo ""
echo "📊 Phase 2: Data Population Validation"
echo "---------------------------------------"

# Test 3: Check if 3 pages exist
python3 << 'EOF'
import sqlite3
import sys

try:
    conn = sqlite3.connect('career_dna.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM pages WHERE is_active = 1")
    page_count = cursor.fetchone()[0]
    
    if page_count != 3:
        print(f"Expected 3 pages, found {page_count}", file=sys.stderr)
        sys.exit(1)
    
    conn.close()
    sys.exit(0)
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

test_result $? "3 consolidated pages exist"

# Test 4: Check if 73 questions exist
python3 << 'EOF'
import sqlite3
import sys

try:
    conn = sqlite3.connect('career_dna.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM questions")
    question_count = cursor.fetchone()[0]
    
    if question_count != 73:
        print(f"Expected 73 questions, found {question_count}", file=sys.stderr)
        sys.exit(1)
    
    conn.close()
    sys.exit(0)
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

test_result $? "73 questions populated"

# Test 5: Check RIASEC page has 27 questions
python3 << 'EOF'
import sqlite3
import sys

try:
    conn = sqlite3.connect('career_dna.db')
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT COUNT(*) FROM questions q
        JOIN pages p ON q.page_id = p.id
        WHERE p.order_index = 1
    """)
    riasec_count = cursor.fetchone()[0]
    
    if riasec_count != 27:
        print(f"Expected 27 RIASEC questions, found {riasec_count}", file=sys.stderr)
        sys.exit(1)
    
    conn.close()
    sys.exit(0)
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

test_result $? "RIASEC page has 27 questions"

# Test 6: Verify unique item_ids
python3 << 'EOF'
import sqlite3
import sys

try:
    conn = sqlite3.connect('career_dna.db')
    cursor = conn.cursor()
    
    cursor.execute("SELECT item_id, COUNT(*) FROM questions GROUP BY item_id HAVING COUNT(*) > 1")
    duplicates = cursor.fetchall()
    
    if duplicates:
        print(f"Duplicate item_ids found: {duplicates}", file=sys.stderr)
        sys.exit(1)
    
    conn.close()
    sys.exit(0)
    
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

test_result $? "All item_ids are unique"

echo ""
echo "🔧 Phase 3: Scoring Engine Validation"
echo "--------------------------------------"

# Test 7: Import v1.1 scoring service
python3 << 'EOF'
import sys
sys.path.append('app')

try:
    from services.scoring_service_v1_1 import (
        calculate_riasec_v1_1,
        calculate_bigfive_v1_1,
        calculate_behavioral_v1_1,
        calculate_ikigai_zones,
        calculate_complete_profile_v1_1
    )
    sys.exit(0)
except ImportError as e:
    print(f"Import error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

test_result $? "v1.1 scoring service imports successfully"

# Test 8: Test strength label thresholds
python3 << 'EOF'
import sys
sys.path.append('app')

try:
    from services.scoring_service_v1_1 import get_strength_label, RIASEC_THRESHOLDS
    
    # Test RIASEC thresholds
    assert get_strength_label(5, RIASEC_THRESHOLDS) == "Low"
    assert get_strength_label(9, RIASEC_THRESHOLDS) == "Medium"
    assert get_strength_label(12, RIASEC_THRESHOLDS) == "High"
    assert get_strength_label(15, RIASEC_THRESHOLDS) == "Very High"
    
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

test_result $? "Strength label thresholds work correctly"

# Test 9: Test reverse scoring
python3 << 'EOF'
import sys
sys.path.append('app')

try:
    from services.scoring_service_v1_1 import apply_reverse_scoring
    
    # Test 5-point scale reverse scoring
    assert apply_reverse_scoring(1, True) == 5
    assert apply_reverse_scoring(2, True) == 4
    assert apply_reverse_scoring(3, True) == 3
    assert apply_reverse_scoring(4, True) == 2
    assert apply_reverse_scoring(5, True) == 1
    assert apply_reverse_scoring(3, False) == 3  # No reverse
    
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

test_result $? "Reverse scoring logic works"

echo ""
echo "🌐 Phase 4: API Endpoint Validation"
echo "------------------------------------"

# Note: These tests require the server to be running
# For now, we'll just check if the files have correct imports

# Test 10: Check API v2 imports
python3 << 'EOF'
import sys
import ast

try:
    with open('app/routers/api_v2.py', 'r') as f:
        tree = ast.parse(f.read())
    
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module and 'scoring_service_v1_1' in node.module:
                imports.extend([alias.name for alias in node.names])
    
    required = ['calculate_complete_profile_v1_1', 'save_assessment_score_v1_1']
    missing = [r for r in required if r not in imports]
    
    if missing:
        print(f"Missing imports in api_v2.py: {missing}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)
except Exception as e:
    print(f"Error: {e}", file=sys.stderr)
    sys.exit(1)
EOF

test_result $? "API v2 imports v1.1 scoring service"

echo ""
echo "🎨 Phase 5: Frontend Component Validation"
echo "------------------------------------------"

# Test 11: Check if SliderQuestion uses 5-point buttons
if grep -q "likert-button" frontend/src/components/questions/SliderQuestion.jsx; then
    test_result 0 "SliderQuestion uses 5-point button interface"
else
    test_result 1 "SliderQuestion still uses old slider"
fi

# Test 12: Check if Results page exists
if [ -f "frontend/src/pages/Results.jsx" ]; then
    test_result 0 "Results page component exists"
else
    test_result 1 "Results page component not found"
fi

# Test 13: Check if App.jsx has Results route
if grep -q "/results/:sessionId" frontend/src/App.jsx; then
    test_result 0 "Results route configured in App.jsx"
else
    test_result 1 "Results route not found in App.jsx"
fi

echo ""
echo "=================================="
echo "📊 Test Summary"
echo "=================================="
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All tests passed! System is ready for v1.1${NC}"
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review and fix issues.${NC}"
    exit 1
fi
