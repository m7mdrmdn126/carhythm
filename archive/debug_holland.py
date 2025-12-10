"""
Debug script to test Holland Code sorting with the exact scores reported by user.
User reported: I (13.8) > R (12.5) > A (11.2) but code shows "RIA" not "IRA"
"""

# Test 1: Direct sorting with user's reported scores
print("=" * 60)
print("TEST 1: User's Reported Scores")
print("=" * 60)

raw_scores = {
    'R': 12.5,
    'I': 13.8,
    'A': 11.2,
    'S': 8.0,
    'E': 9.0,
    'C': 10.0
}

print(f"Raw scores: {raw_scores}")
print()

# This is the EXACT code from line 143
sorted_domains = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
holland_code = "".join([d[0] for d in sorted_domains[:3]])

print(f"Sorted domains: {sorted_domains}")
print(f"Top 3: {sorted_domains[:3]}")
print(f"Holland code: {holland_code}")
print(f"Expected: IRA (I=13.8 > R=12.5 > A=11.2)")
print(f"Match: {'✅ CORRECT' if holland_code == 'IRA' else '❌ WRONG'}")
print()

# Test 2: Check if there's a float precision issue
print("=" * 60)
print("TEST 2: Check Float Precision")
print("=" * 60)

for domain, score in sorted_domains[:3]:
    print(f"{domain}: {score} (type: {type(score).__name__})")
print()

# Test 3: Test with integer scores
print("=" * 60)
print("TEST 3: Integer Scores")
print("=" * 60)

raw_scores_int = {
    'R': 12,
    'I': 14,
    'A': 11,
    'S': 8,
    'E': 9,
    'C': 10
}

sorted_domains_int = sorted(raw_scores_int.items(), key=lambda x: x[1], reverse=True)
holland_code_int = "".join([d[0] for d in sorted_domains_int[:3]])

print(f"Raw scores: {raw_scores_int}")
print(f"Holland code: {holland_code_int}")
print(f"Expected: IRA")
print(f"Match: {'✅ CORRECT' if holland_code_int == 'IRA' else '❌ WRONG'}")
