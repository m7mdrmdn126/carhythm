"""
Feedback Model
Stores user feedback after completing assessments
"""

from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Feedback(Base):
    """Feedback model for storing user assessment feedback"""
    
    __tablename__ = "feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("student_responses.session_id"), nullable=False, index=True)
    rating = Column(Integer, nullable=True)  # 1-5 star rating
    experience_text = Column(Text, nullable=True)  # How was your experience?
    would_recommend = Column(Boolean, nullable=True)  # Would recommend to others?
    suggestions = Column(Text, nullable=True)  # Suggestions for improvement
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationship to response (to get user email and assessment info)
    response = relationship("StudentResponse", back_populates="feedback")
    
    def __repr__(self):
        return f"<Feedback(id={self.id}, session={self.session_id}, rating={self.rating})>"
