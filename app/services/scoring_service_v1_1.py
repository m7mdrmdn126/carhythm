"""
CaRhythm v1.1 Scoring Engine

NEW APPROACH (v1.1):
- Direct sum scoring (no weighted formula)
- Strength labels (Low/Medium/High/Very High)
- Behavioral flags for risk indicators
- Ikigai zone calculations
- 5-point Likert scale (1-5)
"""

from sqlalchemy.orm import Session
from typing import Dict, Optional, List, Tuple
from ..models import StudentResponse, QuestionAnswer, Question, Page, AssessmentScore
import json


# ============================================================================
# STRENGTH LABEL THRESHOLDS
# ============================================================================

RIASEC_THRESHOLDS = {
    "Low": (0, 6),
    "Medium": (7, 10),
    "High": (11, 13),
    "Very High": (14, 15)
}

BIGFIVE_THRESHOLDS = {
    "Low": (0, 10),
    "Medium": (11, 15),
    "High": (16, 20),
    "Very High": (21, 25)
}

BEHAVIORAL_THRESHOLDS = {
    "Low": (0, 6),
    "Medium": (7, 9),
    "High": (10, 12),
    "Very High": (13, 15)
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_strength_label(score: int, thresholds: dict) -> str:
    """Convert raw score to strength label"""
    for label, (min_val, max_val) in thresholds.items():
        if min_val <= score <= max_val:
            return label
    return "Low"  # Default fallback


def apply_reverse_scoring(value: int, is_reversed: bool) -> int:
    """Reverse score if needed (5-point scale: 1↔5, 2↔4, 3↔3)"""
    if not is_reversed:
        return value
    return 6 - value  # 1→5, 2→4, 3→3, 4→2, 5→1


# ============================================================================
# RIASEC SCORING (v1.1)
# ============================================================================

def calculate_riasec_v1_1(db: Session, response_id: int) -> Optional[Dict]:
    """
    Calculate RIASEC scores using v1.1 method:
    - Likert: Direct sum (1-5 scale, 3 items per domain = 3-15 range)
    - Forced Choice: 3 points per selection
    - Ranking: Points based on position (1st=6pts, 2nd=5pts, ..., 6th=1pt)
    - Total per domain: Likert + FC + Ranking
    - Strength labels: Low (0-6), Medium (7-10), High (11-13), Very High (14-15)
    """
    response = db.query(StudentResponse).filter(StudentResponse.id == response_id).first()
    if not response:
        return None
    
    # Get RIASEC page (Page 1)
    riasec_page = db.query(Page).filter(Page.order_index == 1).first()
    if not riasec_page:
        return None
    
    # Get all answers for RIASEC questions
    answers = db.query(QuestionAnswer, Question).join(
        Question, QuestionAnswer.question_id == Question.id
    ).filter(
        QuestionAnswer.response_id == response_id,
        Question.page_id == riasec_page.id
    ).all()
    
    if not answers:
        return None
    
    # Initialize domain scores
    domains = ['R', 'I', 'A', 'S', 'E', 'C']
    raw_scores = {d: 0 for d in domains}
    
    # Process each answer by type
    for answer, question in answers:
        if question.question_type.value == "slider":
            # Likert items: Direct sum (1-5 scale)
            domain = question.domain
            value = answer.answer_value if answer.answer_value else 0
            raw_scores[domain] += value
            
        elif question.question_type.value == "mcq":
            # Forced choice: 3 points per selection
            answer_data = json.loads(answer.answer_json) if answer.answer_json else {}
            selected = answer_data.get('selected_options', [])
            if selected and question.mcq_options:
                options = json.loads(question.mcq_options)
                for opt in options:
                    if opt.get('value') in selected:
                        domain = opt.get('domain')
                        if domain in domains:
                            raw_scores[domain] += 3
                            
        elif question.question_type.value == "ordering":
            # Ranking: 1st=6pts, 2nd=5pts, 3rd=4pts, 4th=3pts, 5th=2pts, 6th=1pt
            answer_data = json.loads(answer.answer_json) if answer.answer_json else {}
            ranking = answer_data.get('ordered_items', [])
            if ranking and question.ordering_options:
                options = json.loads(question.ordering_options)
                for rank_position, item_text in enumerate(ranking):
                    # Find the domain for this item
                    for opt in options:
                        if opt.get('text') == item_text:
                            domain = opt.get('domain')
                            if domain in domains:
                                points = 6 - rank_position  # 1st=6, 2nd=5, etc.
                                raw_scores[domain] += points
                            break
    
    # Convert to strength labels
    strength_labels = {}
    for domain in domains:
        strength_labels[domain] = get_strength_label(raw_scores[domain], RIASEC_THRESHOLDS)
    
    # Determine top 3 Holland Code (sorted by score descending)
    sorted_domains = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
    holland_code = "".join([d[0] for d in sorted_domains[:3]])
    
    return {
        'raw_scores': raw_scores,
        'strength_labels': strength_labels,
        'holland_code': holland_code,
        'top_domain': sorted_domains[0][0] if sorted_domains else None
    }


# ============================================================================
# BIG FIVE SCORING (v1.1)
# ============================================================================

def calculate_bigfive_v1_1(db: Session, response_id: int) -> Optional[Dict]:
    """
    Calculate Big Five scores using v1.1 method:
    - Direct sum of 5 items per trait (1-5 scale, range: 5-25)
    - Apply reverse scoring for N1-N5 (Neuroticism → Emotional Stability)
    - Strength labels: Low (0-10), Medium (11-15), High (16-20), Very High (21-25)
    """
    response = db.query(StudentResponse).filter(StudentResponse.id == response_id).first()
    if not response:
        return None
    
    # Get Big Five page (Page 2)
    bigfive_page = db.query(Page).filter(Page.order_index == 2).first()
    if not bigfive_page:
        return None
    
    # Get all answers for Big Five questions
    answers = db.query(QuestionAnswer, Question).join(
        Question, QuestionAnswer.question_id == Question.id
    ).filter(
        QuestionAnswer.response_id == response_id,
        Question.page_id == bigfive_page.id
    ).all()
    
    if not answers:
        return None
    
    # Initialize trait scores
    traits = ['O', 'C', 'E', 'A', 'N']
    raw_scores = {t: 0 for t in traits}
    
    # Process Likert answers
    for answer, question in answers:
        if question.question_type.value == "slider":
            trait = question.domain
            value = answer.answer_value if answer.answer_value else 0
            
            # Apply reverse scoring if needed
            value = apply_reverse_scoring(value, question.reverse_scored)
            raw_scores[trait] += value
    
    # Convert to strength labels
    strength_labels = {}
    for trait in traits:
        strength_labels[trait] = get_strength_label(raw_scores[trait], BIGFIVE_THRESHOLDS)
    
    return {
        'raw_scores': raw_scores,
        'strength_labels': strength_labels
    }


# ============================================================================
# BEHAVIORAL TRAITS SCORING (v1.1)
# ============================================================================

def calculate_behavioral_v1_1(db: Session, response_id: int) -> Optional[Dict]:
    """
    Calculate Behavioral traits using v1.1 method:
    - Direct sum of 3 items per trait (1-5 scale, range: 3-15)
    - Apply reverse scoring where needed
    - Strength labels: Low (0-6), Medium (7-9), High (10-12), Very High (13-15)
    - Generate behavioral flags (risk indicators)
    """
    response = db.query(StudentResponse).filter(StudentResponse.id == response_id).first()
    if not response:
        return None
    
    # Get Behavioral page (Page 3)
    behavioral_page = db.query(Page).filter(Page.order_index == 3).first()
    if not behavioral_page:
        return None
    
    # Get all answers for Behavioral questions
    answers = db.query(QuestionAnswer, Question).join(
        Question, QuestionAnswer.question_id == Question.id
    ).filter(
        QuestionAnswer.response_id == response_id,
        Question.page_id == behavioral_page.id
    ).all()
    
    if not answers:
        return None
    
    # Initialize trait scores
    traits = ['motivation_type', 'grit_persistence', 'self_efficacy', 
              'resilience', 'learning_orientation', 'empathy', 'task_start_tempo']
    
    raw_scores = {t: 0 for t in traits}
    
    # Process Likert answers
    for answer, question in answers:
        if question.question_type.value == "slider":
            trait = question.domain
            value = answer.answer_value if answer.answer_value else 0
            
            # Apply reverse scoring if needed
            value = apply_reverse_scoring(value, question.reverse_scored)
            raw_scores[trait] += value
    
    # Convert to strength labels
    strength_labels = {}
    for trait in traits:
        strength_labels[trait] = get_strength_label(raw_scores[trait], BEHAVIORAL_THRESHOLDS)
    
    # Generate behavioral flags (risk indicators)
    flags = generate_behavioral_flags(raw_scores, strength_labels)
    
    return {
        'raw_scores': raw_scores,
        'strength_labels': strength_labels,
        'behavioral_flags': flags
    }


# ============================================================================
# BEHAVIORAL FLAGS (Risk Indicators)
# ============================================================================

def generate_behavioral_flags(raw_scores: Dict, strength_labels: Dict) -> Dict:
    """
    Generate behavioral flags based on trait scores:
    - procrastination_risk: Low task_start_tempo
    - perfectionism_risk: Low task_start_tempo + High learning_orientation (fear of mistakes)
    - low_grit_risk: Low grit_persistence
    - poor_regulation_risk: Low self_efficacy
    - growth_mindset: High learning_orientation
    """
    flags = {}
    
    # Procrastination risk: Low task start tempo
    flags['procrastination_risk'] = strength_labels.get('task_start_tempo') == 'Low'
    
    # Perfectionism risk: Low task start + Fear of mistakes
    perfectionism_indicators = (
        strength_labels.get('task_start_tempo') == 'Low' and
        raw_scores.get('learning_orientation', 15) < 9  # Low learning orientation (fear)
    )
    flags['perfectionism_risk'] = perfectionism_indicators
    
    # Low grit risk
    flags['low_grit_risk'] = strength_labels.get('grit_persistence') == 'Low'
    
    # Poor regulation risk: Low self-efficacy
    flags['poor_regulation_risk'] = strength_labels.get('self_efficacy') == 'Low'
    
    # Growth mindset: High learning orientation
    flags['growth_mindset'] = strength_labels.get('learning_orientation') in ['High', 'Very High']
    
    return flags


# ============================================================================
# IKIGAI ZONE CALCULATION
# ============================================================================

def calculate_ikigai_zones(riasec_scores: Dict, bigfive_scores: Dict, behavioral_scores: Dict) -> Dict:
    """
    Map assessment results to Ikigai zones:
    - LOVE (What you love): High RIASEC A (Artistic) + High O (Openness)
    - MASTERY (What you're good at): High RIASEC R/I (Realistic/Investigative) + High C (Conscientiousness)
    - CONTRIBUTION (What the world needs): High RIASEC S (Social) + High A (Agreeableness) + High Empathy
    - SUSTAINABILITY (What you can be paid for): High RIASEC E/C (Enterprising/Conventional) + High Grit
    """
    riasec_raw = riasec_scores.get('raw_scores', {})
    riasec_labels = riasec_scores.get('strength_labels', {})
    bigfive_labels = bigfive_scores.get('strength_labels', {})
    behavioral_labels = behavioral_scores.get('strength_labels', {})
    
    ikigai_zones = {}
    
    # LOVE Zone: Artistic passion + Openness
    love_score = 0
    if riasec_labels.get('A') in ['High', 'Very High']:
        love_score += 2
    if bigfive_labels.get('O') in ['High', 'Very High']:
        love_score += 2
    ikigai_zones['love'] = {
        'score': love_score,
        'level': 'High' if love_score >= 3 else 'Medium' if love_score >= 2 else 'Low'
    }
    
    # MASTERY Zone: Technical/Analytical skills + Conscientiousness
    mastery_score = 0
    if riasec_labels.get('R') in ['High', 'Very High']:
        mastery_score += 1
    if riasec_labels.get('I') in ['High', 'Very High']:
        mastery_score += 1
    if bigfive_labels.get('C') in ['High', 'Very High']:
        mastery_score += 2
    ikigai_zones['mastery'] = {
        'score': mastery_score,
        'level': 'High' if mastery_score >= 3 else 'Medium' if mastery_score >= 2 else 'Low'
    }
    
    # CONTRIBUTION Zone: Social impact + Agreeableness + Empathy
    contribution_score = 0
    if riasec_labels.get('S') in ['High', 'Very High']:
        contribution_score += 2
    if bigfive_labels.get('A') in ['High', 'Very High']:
        contribution_score += 1
    if behavioral_labels.get('empathy') in ['High', 'Very High']:
        contribution_score += 1
    ikigai_zones['contribution'] = {
        'score': contribution_score,
        'level': 'High' if contribution_score >= 3 else 'Medium' if contribution_score >= 2 else 'Low'
    }
    
    # SUSTAINABILITY Zone: Business/Structure + Grit
    sustainability_score = 0
    if riasec_labels.get('E') in ['High', 'Very High']:
        sustainability_score += 1
    if riasec_labels.get('C') in ['High', 'Very High']:
        sustainability_score += 1
    if behavioral_labels.get('grit_persistence') in ['High', 'Very High']:
        sustainability_score += 2
    ikigai_zones['sustainability'] = {
        'score': sustainability_score,
        'level': 'High' if sustainability_score >= 3 else 'Medium' if sustainability_score >= 2 else 'Low'
    }
    
    return ikigai_zones


# ============================================================================
# COMPLETE RHYTHM PROFILE (v1.1)
# ============================================================================

def calculate_complete_profile_v1_1(db: Session, response_id: int) -> Optional[Dict]:
    """
    Generate complete CaRhythm v1.1 profile with:
    - RIASEC raw scores + strength labels
    - Big Five raw scores + strength labels
    - Behavioral raw scores + strength labels + flags
    - Ikigai zones
    - Actionable insights
    """
    # Calculate all three modules
    riasec_results = calculate_riasec_v1_1(db, response_id)
    bigfive_results = calculate_bigfive_v1_1(db, response_id)
    behavioral_results = calculate_behavioral_v1_1(db, response_id)
    
    if not all([riasec_results, bigfive_results, behavioral_results]):
        return None
    
    # Calculate Ikigai zones
    ikigai_zones = calculate_ikigai_zones(riasec_results, bigfive_results, behavioral_results)
    
    # Assemble complete profile
    complete_profile = {
        'riasec': riasec_results,
        'bigfive': bigfive_results,
        'behavioral': behavioral_results,
        'ikigai_zones': ikigai_zones,
        'version': 'v1.1'
    }
    
    return complete_profile


# ============================================================================
# SAVE TO DATABASE
# ============================================================================

def save_assessment_score_v1_1(db: Session, response_id: int, profile: Dict) -> AssessmentScore:
    """
    Save v1.1 assessment results to database using new JSON fields
    """
    response = db.query(StudentResponse).filter(StudentResponse.id == response_id).first()
    if not response:
        return None
    
    # Check if score already exists
    existing_score = db.query(AssessmentScore).filter(
        AssessmentScore.response_id == response_id
    ).first()
    
    if existing_score:
        # Update existing
        score_record = existing_score
    else:
        # Create new
        score_record = AssessmentScore(
            response_id=response_id
        )
        db.add(score_record)
    
    # Store RIASEC scores (keep old fields for compatibility)
    riasec = profile['riasec']
    score_record.riasec_r_score = riasec['raw_scores']['R']
    score_record.riasec_i_score = riasec['raw_scores']['I']
    score_record.riasec_a_score = riasec['raw_scores']['A']
    score_record.riasec_s_score = riasec['raw_scores']['S']
    score_record.riasec_e_score = riasec['raw_scores']['E']
    score_record.riasec_c_score = riasec['raw_scores']['C']
    score_record.riasec_profile = riasec['holland_code']
    
    # Store new v1.1 JSON fields
    score_record.riasec_raw_scores = json.dumps(riasec['raw_scores'])
    score_record.riasec_strength_labels = json.dumps(riasec['strength_labels'])
    
    # Store Big Five scores (use correct field names from model)
    bigfive = profile['bigfive']
    score_record.bigfive_openness = bigfive['raw_scores']['O']
    score_record.bigfive_conscientiousness = bigfive['raw_scores']['C']
    score_record.bigfive_extraversion = bigfive['raw_scores']['E']
    score_record.bigfive_agreeableness = bigfive['raw_scores']['A']
    score_record.bigfive_neuroticism = bigfive['raw_scores']['N']
    score_record.bigfive_strength_labels = json.dumps(bigfive['strength_labels'])
    
    # Store Behavioral scores
    behavioral = profile['behavioral']
    score_record.behavioral_strength_labels = json.dumps(behavioral['strength_labels'])
    score_record.behavioral_flags = json.dumps(behavioral['behavioral_flags'])
    
    # Store Ikigai zones
    score_record.ikigai_zones = json.dumps(profile['ikigai_zones'])
    
    # Store complete rhythm profile
    score_record.rhythm_profile = json.dumps(profile)
    
    db.commit()
    db.refresh(score_record)
    
    return score_record


# ============================================================================
# COMPATIBILITY WRAPPERS (for admin panel)
# ============================================================================

def get_scores_for_response(db: Session, response_id: int) -> Optional[AssessmentScore]:
    """
    Retrieve existing scores for a response.
    Returns None if scores haven't been calculated yet.
    Compatible with old scoring_service API.
    """
    return db.query(AssessmentScore).filter(
        AssessmentScore.response_id == response_id
    ).first()


def calculate_and_save_scores(db: Session, response_id: int) -> AssessmentScore:
    """
    Calculate all v1.1 scores and save them to database.
    Compatible with old scoring_service API.
    """
    profile = calculate_complete_profile_v1_1(db, response_id)
    if not profile:
        raise ValueError(f"Unable to calculate profile for response {response_id}")
    
    return save_assessment_score_v1_1(db, response_id, profile)
