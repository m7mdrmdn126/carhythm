from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class PageBase(BaseModel):
    title: str
    description: Optional[str] = None
    order_index: int = 0
    is_active: bool = True

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