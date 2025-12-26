from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PageBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int = 0
    is_active: bool = True
    # Story Mode / Module Organization fields
    module_name: Optional[str] = None
    module_emoji: Optional[str] = None
    chapter_number: Optional[int] = None
    estimated_minutes: Optional[int] = None
    completion_message: Optional[str] = None
    # Arabic Translation fields
    title_ar: Optional[str] = None
    description_ar: Optional[str] = None
    module_name_ar: Optional[str] = None
    module_description_ar: Optional[str] = None
    completion_message_ar: Optional[str] = None

class PageCreate(PageBase):
    pass

class PageUpdate(PageBase):
    title: Optional[str] = None
    description: Optional[str] = None
    order_index: Optional[int] = None
    is_active: Optional[bool] = None

class Page(PageBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class PageWithQuestions(Page):
    questions: List = []

    class Config:
        from_attributes = True