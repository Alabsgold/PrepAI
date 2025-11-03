from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    source_documents: List["SourceDocument"] = Relationship(back_populates="owner")


class SourceDocument(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    original_filename: str
    file_path: str
    status: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    owner_id: int = Field(foreign_key="user.id")
    owner: "User" = Relationship(back_populates="source_documents")
    generated_quizzes: List["GeneratedQuiz"] = Relationship(
        back_populates="source_document", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class GeneratedQuiz(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    source_document_id: int = Field(foreign_key="sourcedocument.id")
    source_document: "SourceDocument" = Relationship(back_populates="generated_quizzes")
    questions: List["GeneratedQuestion"] = Relationship(
        back_populates="quiz", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class GeneratedQuestion(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    question_text: str
    quiz_id: int = Field(foreign_key="generatedquiz.id")
    quiz: "GeneratedQuiz" = Relationship(back_populates="questions")
    options: List["GeneratedOption"] = Relationship(
        back_populates="question", sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


class GeneratedOption(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    option_text: str
    is_correct: bool
    question_id: int = Field(foreign_key="generatedquestion.id")
    question: "GeneratedQuestion" = Relationship(back_populates="options")
