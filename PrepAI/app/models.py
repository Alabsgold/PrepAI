from typing import Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    source_documents: list["SourceDocument"] = Relationship(back_populates="owner")


class SourceDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_filename: str
    file_path: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: int = Field(foreign_key="user.id")
    owner: User = Relationship(back_populates="source_documents")
    generated_quizzes: list["GeneratedQuiz"] = Relationship(back_populates="source_document")


class GeneratedQuiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_document_id: int = Field(foreign_key="sourcedocument.id")
    source_document: SourceDocument = Relationship(back_populates="generated_quizzes")
    generated_questions: list["GeneratedQuestion"] = Relationship(back_populates="quiz")


class GeneratedQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_text: str
    quiz_id: int = Field(foreign_key="generatedquiz.id")
    quiz: GeneratedQuiz = Relationship(back_populates="generated_questions")
    generated_options: list["GeneratedOption"] = Relationship(back_populates="question")


class GeneratedOption(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    option_text: str
    is_correct: bool
    question_id: int = Field(foreign_key="generatedquestion.id")
    question: GeneratedQuestion = Relationship(back_populates="generated_options")