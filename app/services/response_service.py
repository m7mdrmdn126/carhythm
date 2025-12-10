from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from ..models import StudentResponse, QuestionAnswer, Question, SessionStatus, Page
from ..schemas import StudentResponseCreate, QuestionAnswerCreate
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import uuid

def create_student_response(db: Session, response: StudentResponseCreate) -> StudentResponse:
    """Create a new student response record."""
    db_response = StudentResponse(**response.dict())
    db.add(db_response)
    db.commit()
    db.refresh(db_response)
    return db_response

def get_student_response_by_session(db: Session, session_id: str) -> Optional[StudentResponse]:
    """Get student response by session ID."""
    return db.query(StudentResponse).filter(StudentResponse.session_id == session_id).first()

def complete_student_response(db: Session, session_id: str) -> Optional[StudentResponse]:
    """Mark student response as completed."""
    db_response = db.query(StudentResponse).filter(StudentResponse.session_id == session_id).first()
    if not db_response:
        return None
    
    db_response.completed_at = func.now()
    db.commit()
    db.refresh(db_response)
    return db_response

def create_question_answer(db: Session, answer: QuestionAnswerCreate) -> QuestionAnswer:
    """Create or update a question answer."""
    # Check if answer already exists
    existing_answer = db.query(QuestionAnswer).filter(
        QuestionAnswer.response_id == answer.response_id,
        QuestionAnswer.question_id == answer.question_id
    ).first()
    
    if existing_answer:
        # Update existing answer
        existing_answer.answer_text = answer.answer_text
        existing_answer.answer_value = answer.answer_value
        db.commit()
        # Return existing answer without refresh (already in session)
        return existing_answer
    else:
        # Create new answer
        db_answer = QuestionAnswer(**answer.dict())
        db.add(db_answer)
        db.commit()
        db.refresh(db_answer)
        return db_answer

def get_all_responses(db: Session, skip: int = 0, limit: int = 100) -> List[StudentResponse]:
    """Get all student responses."""
    return db.query(StudentResponse).order_by(StudentResponse.created_at.desc()).offset(skip).limit(limit).all()

def get_response_with_answers(db: Session, response_id: int) -> Optional[StudentResponse]:
    """Get student response with all answers."""
    return db.query(StudentResponse).filter(StudentResponse.id == response_id).first()

def get_answers_by_response(db: Session, response_id: int) -> List[QuestionAnswer]:
    """Get all answers for a specific response."""
    return db.query(QuestionAnswer).filter(QuestionAnswer.response_id == response_id).all()

def delete_student_response(db: Session, response_id: int) -> bool:
    """Delete a student response and all related answers."""
    db_response = db.query(StudentResponse).filter(StudentResponse.id == response_id).first()
    if not db_response:
        return False
    
    db.delete(db_response)
    db.commit()
    return True

def get_response_statistics(db: Session) -> Dict:
    """Get basic statistics about responses."""
    total_responses = db.query(StudentResponse).count()
    completed_responses = db.query(StudentResponse).filter(StudentResponse.completed_at.isnot(None)).count()
    incomplete_responses = total_responses - completed_responses
    
    return {
        "total_responses": total_responses,
        "completed_responses": completed_responses,
        "incomplete_responses": incomplete_responses
    }

def mark_session_abandoned(db: Session, session_id: str) -> bool:
    """Mark session as user_abandoned_not_completed."""
    student_response = get_student_response_by_session(db, session_id)
    if not student_response:
        return False
    
    student_response.status = SessionStatus.abandoned
    db.commit()
    return True

def get_session_progress_info(db: Session, response_id: int) -> Dict:
    """Get detailed progress information for a session."""
    # Get total questions
    total_questions = db.query(Question).join(Page).filter(Page.is_active == True).count()
    
    # Get answered questions
    answered_count = db.query(QuestionAnswer).filter(
        QuestionAnswer.response_id == response_id
    ).count()
    
    percentage = round((answered_count / total_questions * 100), 1) if total_questions > 0 else 0
    total_xp = answered_count * 10
    
    return {
        "questions_answered": answered_count,
        "total_questions": total_questions,
        "percentage": percentage,
        "total_xp": total_xp
    }

def validate_session(db: Session, session_id: str) -> Optional[Dict]:
    """Validate if session exists and is not expired (30 days)."""
    student_response = get_student_response_by_session(db, session_id)
    
    if not student_response:
        return None
    
    # Check if expired (30 days)
    if student_response.last_activity:
        age = datetime.utcnow() - student_response.last_activity
        if age > timedelta(days=30):
            return None
    
    # Get progress info
    progress_info = get_session_progress_info(db, student_response.id)
    
    return {
        "session_id": session_id,
        "response_id": student_response.id,
        "status": student_response.status.value,
        "current_page_id": student_response.current_page_id,
        "last_activity": student_response.last_activity.isoformat() if student_response.last_activity else None,
        "progress": progress_info
    }