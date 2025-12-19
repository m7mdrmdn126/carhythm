from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class Page(Base):
    __tablename__ = "pages"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    order_index = Column(Integer, nullable=False, default=0)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Story Mode / Module Organization fields (optional)
    module_name = Column(String(100))  # e.g., "RIASEC", "Big Five", "Work Rhythm"
    module_emoji = Column(String(10))  # e.g., "🎯", "🧠", "⚡"
    module_description = Column(Text)  # Description shown in module intro
    chapter_number = Column(Integer)  # For ordering modules/chapters
    estimated_minutes = Column(Integer)  # Time estimate for this page
    completion_message = Column(Text)  # Message shown after completing this page
    module_color_primary = Column(String(20))  # Primary theme color e.g., "#8b5cf6"
    module_color_secondary = Column(String(20))  # Secondary theme color e.g., "#3b82f6"
    
    # Relationship with questions
    questions = relationship("Question", back_populates="page", cascade="all, delete-orphan")