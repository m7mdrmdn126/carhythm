"""
⚠️ ARCHIVED - CaRhythm v1.0 Assessment Scoring Service (LEGACY)

This file is archived and superseded by scoring_service_v1_1.py
Last used: CaRhythm v1.0 (11 pages, 0-10 slider, weighted formula)

DO NOT USE THIS FILE - For reference only
Replaced by: app/services/scoring_service_v1_1.py (v1.1 direct sum scoring)

---

CaRhythm Assessment Scoring Service

Implements scoring algorithms for three assessment modules:
1. RIASEC Career Interest (weighted composite: Likert, Forced Choice, Ranking)
2. Big Five Personality (mean × 50 per trait)
3. Work Rhythm Traits (mean × 50 with reverse-keying)

All formulas match the CaRhythm Q Inventory PDF specifications.
"""

from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Dict, Optional, List, Tuple
from ..models import StudentResponse, QuestionAnswer, Question, Page, AssessmentScore
import json


# ============================================================================
# RIASEC SCORING (Holland Code Career Interest)
# ============================================================================

def calculate_riasec_scores(db: Session, response_id: int) -> Optional[Dict]:
    """
    Calculate RIASEC scores from three components:
    - Likert items (18 questions: 3 per type)
    - Forced Choice pairs (6 questions)
    - Ranking sets (3 questions)
    
    Formula: Final = 0.5 × Likert + 0.3 × Forced Choice + 0.2 × Ranking
    Returns dict with R, I, A, S, E, C scores and top 3 profile
    """
    response = db.query(StudentResponse).filter(StudentResponse.id == response_id).first()
    if not response:
        return None
    
    # Get all RIASEC pages (pages 1-7)
    riasec_pages = db.query(Page).filter(Page.order_index.between(1, 7)).all()
    riasec_page_ids = [p.id for p in riasec_pages]
    
    # Get all answers for RIASEC questions
    answers = db.query(QuestionAnswer, Question).join(
        Question, QuestionAnswer.question_id == Question.id
    ).filter(
        QuestionAnswer.response_id == response_id,
        Question.page_id.in_(riasec_page_ids)
    ).all()
    
    if not answers:
        return None
    
    # Separate answers by question type
    likert_answers = []
    forced_choice_answers = []
    ranking_answers = []
    
    for answer, question in answers:
        if question.question_type.value == "slider":
            likert_answers.append((answer, question))
        elif question.question_type.value == "mcq":
            forced_choice_answers.append((answer, question))
        elif question.question_type.value == "ordering":
            ranking_answers.append((answer, question))
    
    # Calculate component scores
    likert_scores = _calculate_riasec_likert(likert_answers)
    forced_choice_scores = _calculate_riasec_forced_choice(forced_choice_answers)
    ranking_scores = _calculate_riasec_ranking(ranking_answers)
    
    # Check if we have complete data
    has_all_components = (likert_scores is not None and 
                         forced_choice_scores is not None and 
                         ranking_scores is not None)
    
    if not has_all_components:
        # Return partial scores or None
        return None
    
    # Weighted combination: 0.5 × Likert + 0.3 × Forced Choice + 0.2 × Ranking
    final_scores = {}
    domains = ['R', 'I', 'A', 'S', 'E', 'C']
    
    for domain in domains:
        likert = likert_scores.get(domain, 0)
        forced = forced_choice_scores.get(domain, 0)
        ranking = ranking_scores.get(domain, 0)
        
        final_scores[domain] = round(0.5 * likert + 0.3 * forced + 0.2 * ranking, 2)
    
    # Determine top 3 profile
    sorted_domains = sorted(final_scores.items(), key=lambda x: x[1], reverse=True)
    profile = "-".join([d[0] for d in sorted_domains[:3]])
    
    return {
        'R': final_scores['R'],
        'I': final_scores['I'],
        'A': final_scores['A'],
        'S': final_scores['S'],
        'E': final_scores['E'],
        'C': final_scores['C'],
        'profile': profile,
        'complete': True
    }


def _calculate_riasec_likert(answers: List[Tuple]) -> Optional[Dict]:
    """
    Calculate RIASEC Likert scores.
    Formula: Mean per type × 50 (scales 0-100 slider to 0-100 score)
    """
    if not answers:
        return None
    
    domain_scores = {'R': [], 'I': [], 'A': [], 'S': [], 'E': [], 'C': []}
    
    for answer, question in answers:
        # Extract domain from question text (format: "[R] Question text...")
        q_text = question.question_text
        if q_text.startswith('[') and ']' in q_text:
            domain = q_text[1:q_text.index(']')]
            if domain in domain_scores and answer.answer_value is not None:
                # Slider is already 0-100, normalize to 0-2 for mean calculation
                normalized = answer.answer_value / 100.0 * 2  # Scale to 0-2
                domain_scores[domain].append(normalized)
    
    # Calculate mean × 50 for each domain
    result = {}
    for domain, values in domain_scores.items():
        if values:
            mean_score = sum(values) / len(values)
            result[domain] = round(mean_score * 50, 2)  # Scale to 0-100
        else:
            result[domain] = 0
    
    return result


def _calculate_riasec_forced_choice(answers: List[Tuple]) -> Optional[Dict]:
    """
    Calculate RIASEC Forced Choice scores.
    Formula: (Count chosen / Total pairs) × 100
    """
    if not answers:
        return None
    
    domain_counts = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
    total_pairs = len(answers)
    
    for answer, question in answers:
        if answer.answer_json:
            try:
                selected = json.loads(answer.answer_json)
                # MCQ options should have domain tags
                options = json.loads(question.mcq_options)
                if isinstance(selected, list) and len(selected) > 0:
                    selected_idx = int(selected[0])
                    if selected_idx < len(options):
                        selected_text = options[selected_idx]
                        # Extract domain from option text
                        if selected_text.startswith('[') and ']' in selected_text:
                            domain = selected_text[1:selected_text.index(']')]
                            if domain in domain_counts:
                                domain_counts[domain] += 1
            except (json.JSONDecodeError, ValueError, IndexError):
                continue
    
    # Calculate proportion × 100
    result = {}
    for domain, count in domain_counts.items():
        if total_pairs > 0:
            result[domain] = round((count / total_pairs) * 100, 2)
        else:
            result[domain] = 0
    
    return result


def _calculate_riasec_ranking(answers: List[Tuple]) -> Optional[Dict]:
    """
    Calculate RIASEC Ranking scores.
    Formula: (7 - rank) points per set, summed, then normalized to 0-100
    """
    if not answers:
        return None
    
    domain_points = {'R': 0, 'I': 0, 'A': 0, 'S': 0, 'E': 0, 'C': 0}
    
    for answer, question in answers:
        if answer.answer_json:
            try:
                ranked_order = json.loads(answer.answer_json)
                options = json.loads(question.ordering_options)
                
                # ranked_order contains indices in the order user ranked them
                for rank, idx in enumerate(ranked_order, start=1):
                    if idx < len(options):
                        option_text = options[idx]
                        # Extract domain from option text
                        if option_text.startswith('[') and ']' in option_text:
                            domain = option_text[1:option_text.index(']')]
                            if domain in domain_points:
                                points = 7 - rank  # Rank 1 gets 6 points, rank 6 gets 1 point
                                domain_points[domain] += points
            except (json.JSONDecodeError, ValueError, IndexError):
                continue
    
    # Normalize to 0-100 scale
    # Max possible: 3 sets × 6 points = 18 points per domain
    max_points = 18
    result = {}
    for domain, points in domain_points.items():
        result[domain] = round((points / max_points) * 100, 2) if max_points > 0 else 0
    
    return result


# ============================================================================
# BIG FIVE PERSONALITY SCORING
# ============================================================================

def calculate_bigfive_scores(db: Session, response_id: int) -> Optional[Dict]:
    """
    Calculate Big Five personality scores.
    Formula: Mean of 8 items × 50 (scales 0-100 slider to 0-100 score)
    Note: Neuroticism item 8 is reverse-keyed
    """
    response = db.query(StudentResponse).filter(StudentResponse.id == response_id).first()
    if not response:
        return None
    
    # Get Big Five pages (pages 8-12)
    bigfive_pages = db.query(Page).filter(Page.order_index.between(8, 12)).order_by(Page.order_index).all()
    
    if len(bigfive_pages) != 5:
        return None
    
    traits = {
        8: 'openness',
        9: 'conscientiousness',
        10: 'extraversion',
        11: 'agreeableness',
        12: 'neuroticism'
    }
    
    scores = {}
    all_complete = True
    
    for page in bigfive_pages:
        trait_name = traits.get(page.order_index)
        if not trait_name:
            continue
        
        # Get all answers for this trait's page
        answers = db.query(QuestionAnswer, Question).join(
            Question, QuestionAnswer.question_id == Question.id
        ).filter(
            QuestionAnswer.response_id == response_id,
            Question.page_id == page.id
        ).all()
        
        if len(answers) != 8:
            all_complete = False
            scores[trait_name] = None
            continue
        
        # Calculate mean score
        values = []
        for idx, (answer, question) in enumerate(answers, start=1):
            if answer.answer_value is not None:
                value = answer.answer_value / 100.0  # Normalize to 0-1
                
                # Reverse-key Neuroticism item 8
                if trait_name == 'neuroticism' and idx == 8:
                    value = 1.0 - value
                
                values.append(value * 2)  # Scale to 0-2 range for calculation
        
        if len(values) == 8:
            mean_score = sum(values) / len(values)
            scores[trait_name] = round(mean_score * 50, 2)  # Scale to 0-100
        else:
            all_complete = False
            scores[trait_name] = None
    
    return {
        'openness': scores.get('openness'),
        'conscientiousness': scores.get('conscientiousness'),
        'extraversion': scores.get('extraversion'),
        'agreeableness': scores.get('agreeableness'),
        'neuroticism': scores.get('neuroticism'),
        'complete': all_complete
    }


# ============================================================================
# WORK RHYTHM TRAITS SCORING
# ============================================================================

def calculate_workrhythm_scores(db: Session, response_id: int) -> Optional[Dict]:
    """
    Calculate Work Rhythm trait scores.
    Formula: Mean of 3 items × 50 (scales 0-100 slider to 0-100 score)
    Note: Various reverse-keyed items per trait (see PDF documentation)
    
    Reverse-keyed items:
    - Motivation: Item 3
    - Grit: Item 3
    - Self-Efficacy: Item 3
    - Resilience: Item 3
    - Learning: Item 3
    - Empathy: None
    - Procrastination: Items 1 & 3
    """
    response = db.query(StudentResponse).filter(StudentResponse.id == response_id).first()
    if not response:
        return None
    
    # Get Work Rhythm pages (pages 13-19)
    workrhythm_pages = db.query(Page).filter(Page.order_index.between(13, 19)).order_by(Page.order_index).all()
    
    if len(workrhythm_pages) != 7:
        return None
    
    traits = {
        13: ('motivation', [3]),           # Item 3 reversed
        14: ('grit', [3]),                 # Item 3 reversed
        15: ('self_efficacy', [3]),        # Item 3 reversed
        16: ('resilience', [3]),           # Item 3 reversed
        17: ('learning', [3]),             # Item 3 reversed
        18: ('empathy', []),               # No reversals
        19: ('procrastination', [1, 3])    # Items 1 & 3 reversed
    }
    
    scores = {}
    all_complete = True
    
    for page in workrhythm_pages:
        trait_info = traits.get(page.order_index)
        if not trait_info:
            continue
        
        trait_name, reverse_items = trait_info
        
        # Get all answers for this trait's page
        answers = db.query(QuestionAnswer, Question).join(
            Question, QuestionAnswer.question_id == Question.id
        ).filter(
            QuestionAnswer.response_id == response_id,
            Question.page_id == page.id
        ).order_by(Question.order_index).all()
        
        if len(answers) != 3:
            all_complete = False
            scores[trait_name] = None
            continue
        
        # Calculate mean score with reverse-keying
        values = []
        for idx, (answer, question) in enumerate(answers, start=1):
            if answer.answer_value is not None:
                value = answer.answer_value / 100.0  # Normalize to 0-1
                
                # Reverse if this item should be reversed
                if idx in reverse_items:
                    value = 1.0 - value
                
                values.append(value * 2)  # Scale to 0-2 range
        
        if len(values) == 3:
            mean_score = sum(values) / len(values)
            scores[trait_name] = round(mean_score * 50, 2)  # Scale to 0-100
        else:
            all_complete = False
            scores[trait_name] = None
    
    return {
        'motivation': scores.get('motivation'),
        'grit': scores.get('grit'),
        'self_efficacy': scores.get('self_efficacy'),
        'resilience': scores.get('resilience'),
        'learning': scores.get('learning'),
        'empathy': scores.get('empathy'),
        'procrastination': scores.get('procrastination'),
        'complete': all_complete
    }


# ============================================================================
# UNIFIED SCORING SERVICE
# ============================================================================

def calculate_all_scores(db: Session, response_id: int) -> Dict:
    """
    Calculate scores for all three assessment modules.
    Returns dict with all scores or None for incomplete modules.
    """
    riasec = calculate_riasec_scores(db, response_id)
    bigfive = calculate_bigfive_scores(db, response_id)
    workrhythm = calculate_workrhythm_scores(db, response_id)
    
    return {
        'riasec': riasec,
        'bigfive': bigfive,
        'workrhythm': workrhythm
    }


def save_scores_to_database(db: Session, response_id: int, scores: Dict) -> AssessmentScore:
    """
    Save calculated scores to the assessment_scores table.
    Creates new record or updates existing one.
    """
    # Check if scores already exist
    existing_score = db.query(AssessmentScore).filter(
        AssessmentScore.response_id == response_id
    ).first()
    
    if existing_score:
        # Update existing record
        score_record = existing_score
    else:
        # Create new record
        score_record = AssessmentScore(response_id=response_id)
        db.add(score_record)
    
    # Update RIASEC scores
    riasec = scores.get('riasec')
    if riasec:
        score_record.riasec_r_score = riasec.get('R')
        score_record.riasec_i_score = riasec.get('I')
        score_record.riasec_a_score = riasec.get('A')
        score_record.riasec_s_score = riasec.get('S')
        score_record.riasec_e_score = riasec.get('E')
        score_record.riasec_c_score = riasec.get('C')
        score_record.riasec_profile = riasec.get('profile')
        score_record.riasec_complete = riasec.get('complete', False)
    
    # Update Big Five scores
    bigfive = scores.get('bigfive')
    if bigfive:
        score_record.bigfive_openness = bigfive.get('openness')
        score_record.bigfive_conscientiousness = bigfive.get('conscientiousness')
        score_record.bigfive_extraversion = bigfive.get('extraversion')
        score_record.bigfive_agreeableness = bigfive.get('agreeableness')
        score_record.bigfive_neuroticism = bigfive.get('neuroticism')
        score_record.bigfive_complete = bigfive.get('complete', False)
    
    # Update Work Rhythm scores
    workrhythm = scores.get('workrhythm')
    if workrhythm:
        score_record.workrhythm_motivation = workrhythm.get('motivation')
        score_record.workrhythm_grit = workrhythm.get('grit')
        score_record.workrhythm_self_efficacy = workrhythm.get('self_efficacy')
        score_record.workrhythm_resilience = workrhythm.get('resilience')
        score_record.workrhythm_learning = workrhythm.get('learning')
        score_record.workrhythm_empathy = workrhythm.get('empathy')
        score_record.workrhythm_procrastination = workrhythm.get('procrastination')
        score_record.workrhythm_complete = workrhythm.get('complete', False)
    
    db.commit()
    db.refresh(score_record)
    return score_record


def get_scores_for_response(db: Session, response_id: int) -> Optional[AssessmentScore]:
    """
    Retrieve existing scores for a response.
    Returns None if scores haven't been calculated yet.
    """
    return db.query(AssessmentScore).filter(
        AssessmentScore.response_id == response_id
    ).first()


def calculate_and_save_scores(db: Session, response_id: int) -> AssessmentScore:
    """
    Calculate all scores and save them to database in one operation.
    This is the main function to use for scoring a response.
    """
    scores = calculate_all_scores(db, response_id)
    return save_scores_to_database(db, response_id, scores)
