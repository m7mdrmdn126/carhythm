from pydantic import BaseModel, validator
from datetime import datetime
from typing import Optional, List
from enum import Enum

class QuestionType(str, Enum):
    essay = "essay"
    slider = "slider"
    mcq = "mcq"
    ordering = "ordering"

# Category Schemas
class CategoryBase(BaseModel):
    name: str
    description: Optional[str] = None
    color: str = "#3498db"
    is_active: bool = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None

class Category(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# Question Pool Schemas
class QuestionPoolBase(BaseModel):
    title: str
    question_text: str
    question_type: QuestionType
    category_id: Optional[int] = None
    is_required: bool = True
    image_path: Optional[str] = None
    
    # Essay fields
    essay_char_limit: Optional[int] = None
    
    # Slider fields
    slider_min_label: Optional[str] = None
    slider_max_label: Optional[str] = None
    
    # MCQ fields
    mcq_options: Optional[List[str]] = None
    mcq_correct_answer: Optional[List[int]] = None
    allow_multiple_selection: Optional[bool] = False
    
    # Ordering fields
    ordering_options: Optional[List[str]] = None
    randomize_order: Optional[bool] = True

    @validator('mcq_options')
    def validate_mcq_options(cls, v, values):
        if values.get('question_type') == 'mcq' and (not v or len(v) < 2):
            raise ValueError('MCQ questions must have at least 2 options')
        return v
    
    @validator('mcq_correct_answer')
    def validate_mcq_correct_answer(cls, v, values):
        if values.get('question_type') == 'mcq' and (not v or len(v) < 1):
            raise ValueError('MCQ questions must have at least 1 correct answer')
        return v
    
    @validator('ordering_options')
    def validate_ordering_options(cls, v, values):
        if values.get('question_type') == 'ordering' and (not v or len(v) < 2):
            raise ValueError('Ordering questions must have at least 2 items')
        return v

class QuestionPoolCreate(QuestionPoolBase):
    created_by: Optional[str] = None

class QuestionPoolUpdate(BaseModel):
    title: Optional[str] = None
    question_text: Optional[str] = None
    question_type: Optional[QuestionType] = None
    category_id: Optional[int] = None
    is_required: Optional[bool] = None
    image_path: Optional[str] = None
    
    # Essay fields
    essay_char_limit: Optional[int] = None
    
    # Slider fields
    slider_min_label: Optional[str] = None
    slider_max_label: Optional[str] = None
    
    # MCQ fields
    mcq_options: Optional[List[str]] = None
    mcq_correct_answer: Optional[List[int]] = None
    allow_multiple_selection: Optional[bool] = None
    
    # Ordering fields
    ordering_options: Optional[List[str]] = None
    randomize_order: Optional[bool] = None

class QuestionPool(QuestionPoolBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: Optional[str]
    usage_count: int
    category: Optional[Category] = None
    
    class Config:
        from_attributes = True

# Assignment Schemas
class QuestionPageAssignmentBase(BaseModel):
    question_pool_id: int
    page_id: int
    order_index: int = 0

class QuestionPageAssignmentCreate(QuestionPageAssignmentBase):
    assigned_by: Optional[str] = None

class QuestionPageAssignment(QuestionPageAssignmentBase):
    id: int
    assigned_at: datetime
    assigned_by: Optional[str]
    question: Optional[QuestionPool] = None
    
    class Config:
        from_attributes = True

# Import/Export Schemas
class CSVImportResult(BaseModel):
    total_rows: int
    successful_imports: int
    failed_imports: int
    errors: List[dict]
    import_log_id: int

class BulkOperationRequest(BaseModel):
    question_ids: List[int]
    operation: str  # 'assign', 'unassign', 'delete', 'export'
    page_id: Optional[int] = None  # For assign/unassign operations

# Search and Filter Schemas
class QuestionPoolFilter(BaseModel):
    category_id: Optional[int] = None
    question_type: Optional[QuestionType] = None
    search_text: Optional[str] = None
    created_by: Optional[str] = None
    usage_min: Optional[int] = None
    usage_max: Optional[int] = None
    skip: int = 0
    limit: int = 50

class QuestionPoolStats(BaseModel):
    total_questions: int
    by_type: dict
    by_category: dict
    most_used: List[dict]
    recent_imports: List[dict]