from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models import Page, Question
from ..schemas import PageCreate, PageUpdate, QuestionCreate, QuestionUpdate
from typing import List, Optional
import json

def create_page(db: Session, page: PageCreate) -> Page:
    """Create a new question page."""
    db_page = Page(**page.dict())
    db.add(db_page)
    db.commit()
    db.refresh(db_page)
    return db_page

def get_pages(db: Session, skip: int = 0, limit: int = 100, active_only: bool = False) -> List[Page]:
    """Get all pages with optional filtering."""
    query = db.query(Page).order_by(Page.order_index)
    if active_only:
        query = query.filter(Page.is_active == True)
    return query.offset(skip).limit(limit).all()

def get_page_by_id(db: Session, page_id: int) -> Optional[Page]:
    """Get a page by ID."""
    return db.query(Page).filter(Page.id == page_id).first()

def update_page(db: Session, page_id: int, page_update: PageUpdate) -> Optional[Page]:
    """Update a page."""
    db_page = db.query(Page).filter(Page.id == page_id).first()
    if not db_page:
        return None
    
    update_data = page_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_page, field, value)
    
    db.commit()
    db.refresh(db_page)
    return db_page

def delete_page(db: Session, page_id: int) -> bool:
    """Delete a page."""
    db_page = db.query(Page).filter(Page.id == page_id).first()
    if not db_page:
        return False
    
    db.delete(db_page)
    db.commit()
    return True

def create_question(db: Session, question: QuestionCreate) -> Question:
    """Create a new question."""
    question_data = question.dict()
    
    # Convert list fields to JSON strings for database storage
    if question_data.get('mcq_options'):
        question_data['mcq_options'] = json.dumps(question_data['mcq_options'])
    if question_data.get('mcq_correct_answer'):
        question_data['mcq_correct_answer'] = json.dumps(question_data['mcq_correct_answer'])
    if question_data.get('ordering_options'):
        question_data['ordering_options'] = json.dumps(question_data['ordering_options'])
    
    db_question = Question(**question_data)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return db_question

def get_questions_by_page(db: Session, page_id: int) -> List[Question]:
    """Get all questions for a specific page."""
    questions = db.query(Question).filter(Question.page_id == page_id).order_by(Question.order_index).all()
    # Parse JSON fields for each question
    for question in questions:
        # Parse MCQ options
        if question.mcq_options:
            try:
                question.mcq_options_parsed = json.loads(question.mcq_options)
            except (json.JSONDecodeError, TypeError):
                question.mcq_options_parsed = []
        else:
            question.mcq_options_parsed = []
            
        # Parse MCQ correct answers
        if question.mcq_correct_answer:
            try:
                question.mcq_correct_answers_parsed = json.loads(question.mcq_correct_answer)
            except (json.JSONDecodeError, TypeError):
                question.mcq_correct_answers_parsed = []
        else:
            question.mcq_correct_answers_parsed = []
            
        # Parse ordering options
        if question.ordering_options:
            try:
                parsed_options = json.loads(question.ordering_options)
                # Randomize if enabled (for new sessions)
                if question.randomize_order and question.question_type == "ordering":
                    import random
                    question.ordering_options_parsed = random.sample(parsed_options, len(parsed_options))
                else:
                    question.ordering_options_parsed = parsed_options
            except (json.JSONDecodeError, TypeError):
                question.ordering_options_parsed = []
        else:
            question.ordering_options_parsed = []
    
    return questions

def get_question_by_id(db: Session, question_id: int) -> Optional[Question]:
    """Get a question by ID."""
    return db.query(Question).filter(Question.id == question_id).first()

def update_question(db: Session, question_id: int, question_update: QuestionUpdate) -> Optional[Question]:
    """Update a question."""
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        return None
    
    update_data = question_update.dict(exclude_unset=True)
    
    # Convert list fields to JSON strings for database storage
    if 'mcq_options' in update_data and update_data['mcq_options'] is not None:
        update_data['mcq_options'] = json.dumps(update_data['mcq_options'])
    if 'mcq_correct_answer' in update_data and update_data['mcq_correct_answer'] is not None:
        update_data['mcq_correct_answer'] = json.dumps(update_data['mcq_correct_answer'])
    if 'ordering_options' in update_data and update_data['ordering_options'] is not None:
        update_data['ordering_options'] = json.dumps(update_data['ordering_options'])
    
    for field, value in update_data.items():
        setattr(db_question, field, value)
    
    db.commit()
    db.refresh(db_question)
    return db_question

def delete_question(db: Session, question_id: int) -> bool:
    """Delete a question."""
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        return False
    
    db.delete(db_question)
    db.commit()
    return True

def update_question_image(db: Session, question_id: int, image_path: Optional[str]) -> Optional[Question]:
    """Update question image path."""
    db_question = db.query(Question).filter(Question.id == question_id).first()
    if not db_question:
        return None
    
    db_question.image_path = image_path
    db.commit()
    db.refresh(db_question)
    return db_question

def serialize_question_for_response(question: Question) -> dict:
    """Convert database question to response format with JSON field parsing."""
    question_dict = {
        "id": question.id,
        "page_id": question.page_id,
        "question_text": question.question_text,
        "question_type": question.question_type,
        "order_index": question.order_index,
        "is_required": question.is_required,
        "image_path": question.image_path,
        "created_at": question.created_at,
        "slider_min_label": question.slider_min_label,
        "slider_max_label": question.slider_max_label,
        "essay_char_limit": question.essay_char_limit,
        "allow_multiple_selection": question.allow_multiple_selection,
        "randomize_order": question.randomize_order,
    }
    
    # Parse JSON fields
    try:
        question_dict["mcq_options"] = json.loads(question.mcq_options) if question.mcq_options else None
    except (json.JSONDecodeError, TypeError):
        question_dict["mcq_options"] = None
        
    try:
        question_dict["mcq_correct_answer"] = json.loads(question.mcq_correct_answer) if question.mcq_correct_answer else None
    except (json.JSONDecodeError, TypeError):
        question_dict["mcq_correct_answer"] = None
        
    try:
        question_dict["ordering_options"] = json.loads(question.ordering_options) if question.ordering_options else None
    except (json.JSONDecodeError, TypeError):
        question_dict["ordering_options"] = None
    
    return question_dict