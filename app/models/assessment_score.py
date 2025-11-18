from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class AssessmentScore(Base):
    """
    Stores calculated scores for all three assessment modules:
    - RIASEC (Career Interest)
    - Big Five (Personality)
    - Work Rhythm (Work Traits)
    """
    __tablename__ = "assessment_scores"

    id = Column(Integer, primary_key=True, index=True)
    response_id = Column(Integer, ForeignKey("student_responses.id"), nullable=False, unique=True)
    
    # RIASEC Career Interest Scores (0-100 for each domain)
    riasec_r_score = Column(Float)  # Realistic
    riasec_i_score = Column(Float)  # Investigative
    riasec_a_score = Column(Float)  # Artistic
    riasec_s_score = Column(Float)  # Social
    riasec_e_score = Column(Float)  # Enterprising
    riasec_c_score = Column(Float)  # Conventional
    riasec_profile = Column(String(20))  # Top 3 codes (e.g., "R-I-A")
    riasec_complete = Column(Boolean, default=False)  # Module completion flag
    
    # Big Five Personality Scores (0-100 for each trait)
    bigfive_openness = Column(Float)
    bigfive_conscientiousness = Column(Float)
    bigfive_extraversion = Column(Float)
    bigfive_agreeableness = Column(Float)
    bigfive_neuroticism = Column(Float)
    bigfive_complete = Column(Boolean, default=False)
    
    # Work Rhythm Trait Scores (0-100 for each trait)
    workrhythm_motivation = Column(Float)
    workrhythm_grit = Column(Float)
    workrhythm_self_efficacy = Column(Float)
    workrhythm_resilience = Column(Float)
    workrhythm_learning = Column(Float)
    workrhythm_empathy = Column(Float)
    workrhythm_procrastination = Column(Float)
    workrhythm_complete = Column(Boolean, default=False)
    
    # Metadata
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    notes = Column(Text)  # For any special notes or warnings
    
    # Relationships
    response = relationship("StudentResponse", back_populates="scores")
