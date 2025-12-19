"""
Feedback Router
API endpoints for submitting and managing user feedback
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime
import logging

from ..models import get_db, Feedback, StudentResponse as Response
from ..schemas.feedback import (
    FeedbackSubmit, 
    FeedbackResponse, 
    FeedbackWithDetails,
    FeedbackStats
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/feedback", tags=["feedback"])


@router.post("/submit", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def submit_feedback(
    feedback_data: FeedbackSubmit,
    db: Session = Depends(get_db)
):
    """
    Submit feedback after completing an assessment.
    All fields are optional.
    """
    try:
        # Verify session exists
        response = db.query(Response).filter(
            Response.session_id == feedback_data.session_id
        ).first()
        
        if not response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Check if feedback already exists for this session
        existing_feedback = db.query(Feedback).filter(
            Feedback.session_id == feedback_data.session_id
        ).first()
        
        if existing_feedback:
            # Update existing feedback
            if feedback_data.rating is not None:
                existing_feedback.rating = feedback_data.rating
            if feedback_data.experience_text is not None:
                existing_feedback.experience_text = feedback_data.experience_text
            if feedback_data.would_recommend is not None:
                existing_feedback.would_recommend = feedback_data.would_recommend
            if feedback_data.suggestions is not None:
                existing_feedback.suggestions = feedback_data.suggestions
            
            db.commit()
            db.refresh(existing_feedback)
            
            logger.info(f"Updated feedback for session {feedback_data.session_id}")
            return existing_feedback
        
        # Create new feedback
        new_feedback = Feedback(
            session_id=feedback_data.session_id,
            rating=feedback_data.rating,
            experience_text=feedback_data.experience_text,
            would_recommend=feedback_data.would_recommend,
            suggestions=feedback_data.suggestions,
            created_at=datetime.utcnow()
        )
        
        db.add(new_feedback)
        db.commit()
        db.refresh(new_feedback)
        
        logger.info(f"Created feedback for session {feedback_data.session_id}")
        return new_feedback
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting feedback: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to submit feedback"
        )


@router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats(db: Session = Depends(get_db)):
    """
    Get feedback statistics (for admin dashboard).
    """
    try:
        total_feedbacks = db.query(func.count(Feedback.id)).scalar() or 0
        
        # Average rating (only counting feedbacks with ratings)
        avg_rating = db.query(func.avg(Feedback.rating)).filter(
            Feedback.rating.isnot(None)
        ).scalar()
        
        total_with_rating = db.query(func.count(Feedback.id)).filter(
            Feedback.rating.isnot(None)
        ).scalar() or 0
        
        # Recommendation counts
        would_recommend = db.query(func.count(Feedback.id)).filter(
            Feedback.would_recommend == True
        ).scalar() or 0
        
        would_not_recommend = db.query(func.count(Feedback.id)).filter(
            Feedback.would_recommend == False
        ).scalar() or 0
        
        return FeedbackStats(
            total_feedbacks=total_feedbacks,
            average_rating=round(avg_rating, 2) if avg_rating else None,
            would_recommend_count=would_recommend,
            would_not_recommend_count=would_not_recommend,
            total_with_rating=total_with_rating
        )
        
    except Exception as e:
        logger.error(f"Error getting feedback stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get feedback statistics"
        )


@router.get("/list", response_model=List[FeedbackWithDetails])
async def list_feedbacks(
    limit: int = 100,
    offset: int = 0,
    rating: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    List all feedbacks with user details (for admin).
    """
    try:
        query = db.query(Feedback).join(Response)
        
        # Filter by rating if specified
        if rating is not None:
            query = query.filter(Feedback.rating == rating)
        
        # Order by most recent first
        query = query.order_by(desc(Feedback.created_at))
        
        # Pagination
        feedbacks = query.offset(offset).limit(limit).all()
        
        # Build response with user details
        result = []
        for feedback in feedbacks:
            feedback_dict = {
                "id": feedback.id,
                "session_id": feedback.session_id,
                "rating": feedback.rating,
                "experience_text": feedback.experience_text,
                "would_recommend": feedback.would_recommend,
                "suggestions": feedback.suggestions,
                "created_at": feedback.created_at,
                "user_email": feedback.response.email if feedback.response else None,
                "user_name": feedback.response.full_name if feedback.response else None,
                "assessment_type": "Career DNA Assessment"  # Could be dynamic based on assessment type
            }
            result.append(FeedbackWithDetails(**feedback_dict))
        
        return result
        
    except Exception as e:
        logger.error(f"Error listing feedbacks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list feedbacks"
        )
