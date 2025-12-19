"""
Feedback Schemas
Pydantic models for feedback request/response validation
"""

from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class FeedbackSubmit(BaseModel):
    """Schema for submitting feedback"""
    session_id: str = Field(..., description="Session ID for the assessment")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Rating from 1-5 stars")
    experience_text: Optional[str] = Field(None, max_length=2000, description="User's experience description")
    would_recommend: Optional[bool] = Field(None, description="Would recommend to others")
    suggestions: Optional[str] = Field(None, max_length=2000, description="Suggestions for improvement")
    
    @validator('experience_text', 'suggestions')
    def strip_whitespace(cls, v):
        """Strip whitespace from text fields"""
        if v:
            return v.strip()
        return v


class FeedbackResponse(BaseModel):
    """Schema for feedback response"""
    id: int
    session_id: str
    rating: Optional[int]
    experience_text: Optional[str]
    would_recommend: Optional[bool]
    suggestions: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class FeedbackWithDetails(FeedbackResponse):
    """Schema for feedback with user details (for admin)"""
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    assessment_type: Optional[str] = None
    
    class Config:
        from_attributes = True


class FeedbackStats(BaseModel):
    """Schema for feedback statistics"""
    total_feedbacks: int
    average_rating: Optional[float]
    would_recommend_count: int
    would_not_recommend_count: int
    total_with_rating: int
