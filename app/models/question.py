from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import enum

class QuestionType(enum.Enum):
    essay = "essay"
    slider = "slider"
    mcq = "mcq"           # Multiple Choice Questions
    ordering = "ordering"  # Ordering Questions

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(Enum(QuestionType), nullable=False)
    image_path = Column(String(255))
    order_index = Column(Integer, nullable=False, default=0)
    is_required = Column(Boolean, default=True, nullable=False)
    
    # CaRhythm v1.1 fields
    item_id = Column(String(20), unique=True, index=True)  # e.g., "R1", "FC_RI_1", "RANK1"
    domain = Column(String(20))  # RIASEC domain (R/I/A/S/E/C) or trait code
    tags = Column(Text)  # JSON array of behavioral tags
    reverse_scored = Column(Boolean, default=False)  # For reverse-keyed items
    scale_type = Column(String(20))  # "likert_5", "forced_choice", "ranking"
    scale_labels = Column(Text)  # JSON array: ["Not at all", "A little", ...]
    
    # Essay question fields
    essay_char_limit = Column(Integer)  # For essay questions
    
    # Slider question fields
    slider_min_label = Column(String(100))  # For slider questions
    slider_max_label = Column(String(100))  # For slider questions
    
    # MCQ question fields
    mcq_options = Column(Text)  # JSON string: ["Option A", "Option B", "Option C"]
    mcq_correct_answer = Column(Text)  # JSON string: ["0"] for single, ["0","2"] for multi
    allow_multiple_selection = Column(Boolean, default=False)  # Single vs multiple choice
    
    # Ordering question fields
    ordering_options = Column(Text)  # JSON string: ["Item 1", "Item 2", "Item 3"]
    randomize_order = Column(Boolean, default=True)  # Randomize initial order
    
    # Story Mode fields (optional - for enhanced UX)
    scene_title = Column(String(200))  # e.g., "THE WORKSHOP DISCOVERY"
    scene_narrative = Column(Text)  # Story context for the question
    scene_image_url = Column(String(500))  # Background image/GIF URL for scene
    scene_theme = Column(String(50))  # Color theme: workshop/mindpalace/flow
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    page = relationship("Page", back_populates="questions")
    answers = relationship("QuestionAnswer", back_populates="question", cascade="all, delete-orphan")