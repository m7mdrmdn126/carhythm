from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List
from enum import Enum

class QuestionType(str, Enum):
    essay = "essay"
    slider = "slider"
    mcq = "mcq"
    ordering = "ordering"

class QuestionBase(BaseModel):
    page_id: int
    question_text: str
    question_type: QuestionType
    order_index: int = 0
    is_required: bool = True
    slider_min_label: Optional[str] = None
    slider_max_label: Optional[str] = None
    essay_char_limit: Optional[int] = None
    # MCQ fields
    mcq_options: Optional[List[str]] = None
    mcq_correct_answer: Optional[List[int]] = None
    allow_multiple_selection: Optional[bool] = False
    # Ordering fields
    ordering_options: Optional[List[str]] = None
    randomize_order: Optional[bool] = True
    # Story Mode fields
    scene_title: Optional[str] = None
    scene_narrative: Optional[str] = None
    scene_image_url: Optional[str] = None
    scene_theme: Optional[str] = None
    # Arabic Translation fields
    question_text_ar: Optional[str] = None
    slider_min_label_ar: Optional[str] = None
    slider_max_label_ar: Optional[str] = None
    mcq_options_ar: Optional[List[str]] = None
    ordering_options_ar: Optional[List[str]] = None
    scene_title_ar: Optional[str] = None
    scene_narrative_ar: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    question_type: Optional[QuestionType] = None
    order_index: Optional[int] = None
    is_required: Optional[bool] = None
    slider_min_label: Optional[str] = None
    slider_max_label: Optional[str] = None
    essay_char_limit: Optional[int] = None
    # MCQ fields
    mcq_options: Optional[List[str]] = None
    mcq_correct_answer: Optional[List[int]] = None
    allow_multiple_selection: Optional[bool] = None
    # Ordering fields
    ordering_options: Optional[List[str]] = None
    randomize_order: Optional[bool] = None
    # Story Mode fields
    scene_title: Optional[str] = None
    scene_narrative: Optional[str] = None
    scene_image_url: Optional[str] = None
    scene_theme: Optional[str] = None
    # Arabic Translation fields
    question_text_ar: Optional[str] = None
    slider_min_label_ar: Optional[str] = None
    slider_max_label_ar: Optional[str] = None
    mcq_options_ar: Optional[List[str]] = None
    ordering_options_ar: Optional[List[str]] = None
    scene_title_ar: Optional[str] = None
    scene_narrative_ar: Optional[str] = None

class Question(QuestionBase):
    id: int
    image_path: Optional[str] = None
    created_at: datetime
    # MCQ fields
    mcq_options: Optional[List[str]] = None
    mcq_correct_answer: Optional[List[int]] = None
    allow_multiple_selection: Optional[bool] = None
    # Ordering fields
    ordering_options: Optional[List[str]] = None
    randomize_order: Optional[bool] = None

    class Config:
        from_attributes = True