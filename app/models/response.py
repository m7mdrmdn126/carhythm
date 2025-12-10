from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class SessionStatus(enum.Enum):
    """Session status enumeration"""
    active = "active"
    completed = "completed"
    abandoned = "user_abandoned_not_completed"

class StudentResponse(Base):
    __tablename__ = "student_responses"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True, nullable=False)  # UUID
    email = Column(String(255), nullable=False)
    full_name = Column(String(200), nullable=False)
    age_group = Column(String(50), nullable=False)
    country = Column(String(100), nullable=False)
    origin_country = Column(String(100), nullable=False)
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Progress tracking fields
    status = Column(Enum(SessionStatus), default=SessionStatus.active, nullable=False, index=True)
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    current_page_id = Column(Integer, ForeignKey("pages.id"), nullable=True)
    
    # Relationships
    answers = relationship("QuestionAnswer", back_populates="response", cascade="all, delete-orphan")
    scores = relationship("AssessmentScore", back_populates="response", uselist=False, cascade="all, delete-orphan")
    current_page = relationship("Page", foreign_keys=[current_page_id])

class QuestionAnswer(Base):
    __tablename__ = "question_answers"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("student_responses.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer_text = Column(Text)  # For essay questions
    answer_value = Column(Float)  # For slider questions (0-100)
    answer_json = Column(Text)  # For complex answers (MCQ, ordering) - JSON format
    
    # Relationships
    response = relationship("StudentResponse", back_populates="answers")
    question = relationship("Question", back_populates="answers")