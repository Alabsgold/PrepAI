from pydantic import BaseModel
from datetime import datetime
from typing import List


class UserCreate(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: int
    username: str


class OptionRead(BaseModel):
    id: int
    option_text: str
    is_correct: bool

    class Config:
        from_attributes = True


class QuestionRead(BaseModel):
    id: int
    question_text: str
    options: List[OptionRead]

    class Config:
        from_attributes = True


class QuizRead(BaseModel):
    id: int
    title: str
    source_document_id: int
    questions: List[QuestionRead]

    class Config:
        from_attributes = True


class DocumentRead(BaseModel):
    id: int
    original_filename: str
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
