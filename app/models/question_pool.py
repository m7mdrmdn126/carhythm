from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

class Category(Base):
    """Question categories for organizing the question pool."""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    color = Column(String(7), default="#3498db")  # Hex color code
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)
    
    # Relationships
    questions = relationship("QuestionPool", back_populates="category")

class QuestionPool(Base):
    """Central repository for all questions."""
    __tablename__ = "question_pool"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(20), nullable=False)  # essay, slider, mcq, ordering
    category_id = Column(Integer, ForeignKey("categories.id"))
    
    # Common fields
    is_required = Column(Boolean, default=True)
    image_path = Column(String(255))
    
    # Essay fields
    essay_char_limit = Column(Integer)
    
    # Slider fields
    slider_min_label = Column(String(100))
    slider_max_label = Column(String(100))
    
    # MCQ fields
    mcq_options = Column(Text)  # JSON string
    mcq_correct_answer = Column(Text)  # JSON string
    allow_multiple_selection = Column(Boolean, default=False)
    
    # Ordering fields
    ordering_options = Column(Text)  # JSON string
    randomize_order = Column(Boolean, default=True)
    
    # Arabic Translation fields
    question_text_ar = Column(Text)  # Arabic translation of question text
    slider_min_label_ar = Column(String(100))  # Arabic slider minimum label
    slider_max_label_ar = Column(String(100))  # Arabic slider maximum label
    mcq_options_ar = Column(Text)  # JSON array of Arabic MCQ options
    ordering_options_ar = Column(Text)  # JSON array of Arabic ordering options
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    created_by = Column(String(100))
    usage_count = Column(Integer, default=0)
    
    # Relationships
    category = relationship("Category", back_populates="questions")
    assignments = relationship("QuestionPageAssignment", back_populates="question")

class QuestionPageAssignment(Base):
    """Links questions from the pool to specific pages."""
    __tablename__ = "question_page_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    question_pool_id = Column(Integer, ForeignKey("question_pool.id"), nullable=False)
    page_id = Column(Integer, ForeignKey("pages.id"), nullable=False)
    order_index = Column(Integer, default=0)
    assigned_at = Column(DateTime(timezone=True), server_default=func.now())
    assigned_by = Column(String(100))
    
    # Relationships
    question = relationship("QuestionPool", back_populates="assignments")
    page = relationship("Page")

class ImportLog(Base):
    """Tracks CSV import operations."""
    __tablename__ = "import_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    import_type = Column(String(50), nullable=False)  # essay, slider, mcq, ordering
    total_rows = Column(Integer, default=0)
    successful_imports = Column(Integer, default=0)
    failed_imports = Column(Integer, default=0)
    errors = Column(Text)  # JSON string of errors
    imported_by = Column(String(100))
    imported_at = Column(DateTime(timezone=True), server_default=func.now())