from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List

class StudentResponseBase(BaseModel):
    email: EmailStr
    full_name: str
    age_group: str
    country: str
    origin_country: str

class StudentResponseCreate(StudentResponseBase):
    session_id: str

class StudentResponse(StudentResponseBase):
    id: int
    session_id: str
    completed_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True

class QuestionAnswerBase(BaseModel):
    question_id: int
    answer_text: Optional[str] = None
    answer_value: Optional[float] = None
    answer_json: Optional[str] = None

class QuestionAnswerCreate(QuestionAnswerBase):
    response_id: int

class QuestionAnswer(QuestionAnswerBase):
    id: int
    response_id: int

    class Config:
        from_attributes = True

class StudentResponseWithAnswers(StudentResponse):
    answers: List[QuestionAnswer] = []

    class Config:
        from_attributes = True

class ExamSession(BaseModel):
    session_id: str
    current_page: int = 0
    answers: dict = {}

class SubmitAnswer(BaseModel):
    question_id: int
    answer_text: Optional[str] = None
    answer_value: Optional[float] = None