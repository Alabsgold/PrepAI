import uuid
import fitz  # PyMuPDF
from pathlib import Path
from fastapi import Depends, HTTPException, UploadFile
from sqlmodel import Session, select
from passlib.context import CryptContext

from .database import get_session
from .models import User, SourceDocument, GeneratedQuiz, GeneratedQuestion
from .schemas import UserCreate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    def create_user(self, user_create: UserCreate) -> User:
        statement = select(User).where(User.username == user_create.username)
        existing_user = self.session.exec(statement).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already registered")

        hashed_password = pwd_context.hash(user_create.password)
        db_user = User(username=user_create.username, hashed_password=hashed_password)

        self.session.add(db_user)
        self.session.commit()
        self.session.refresh(db_user)

        return db_user

    def get_user_by_username(self, username: str) -> User | None:
        statement = select(User).where(User.username == username)
        return self.session.exec(statement).first()


class DocumentService:
    def __init__(self, session: Session = Depends(get_session)):
        self.session = session

    async def create_upload_document(self, file: UploadFile, current_user: User) -> SourceDocument:
        upload_dir = Path("media/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)

        sanitized_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = upload_dir / sanitized_filename

        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        db_document = SourceDocument(
            original_filename=file.filename,
            file_path=str(file_path),
            status="PENDING",
            owner_id=current_user.id,
        )
        self.session.add(db_document)
        self.session.commit()
        self.session.refresh(db_document)

        from .tasks import process_document_task
        process_document_task.delay(db_document.id)

        return db_document

    def extract_text_from_document(self, file_path: str) -> str:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text

    def get_document_by_id(self, document_id: int, user_id: int) -> SourceDocument | None:
        statement = select(SourceDocument).where(SourceDocument.id == document_id, SourceDocument.owner_id == user_id)
        return self.session.exec(statement).first()

    def get_all_documents_for_user(self, user_id: int) -> list[SourceDocument]:
        statement = select(SourceDocument).where(SourceDocument.owner_id == user_id)
        return self.session.exec(statement).all()

    def get_quiz_for_document(self, document_id: int, user_id: int):
        document = self.get_document_by_id(document_id, user_id)
        if not document:
            return None

        from sqlalchemy.orm import selectinload
        statement = (
            select(GeneratedQuiz)
            .where(GeneratedQuiz.source_document_id == document.id)
            .options(
                selectinload(GeneratedQuiz.questions)
                .selectinload(GeneratedQuestion.options)
            )
        )
        quiz = self.session.exec(statement).unique().first()
        return quiz

    def delete_document_by_id(self, document_id: int, user_id: int) -> bool:
        document = self.get_document_by_id(document_id, user_id)
        if not document:
            return False

        # Delete the file from the filesystem
        try:
            Path(document.file_path).unlink()
        except FileNotFoundError:
            # Log this, but don't fail the operation if the file is already gone
            print(f"File not found, could not delete: {document.file_path}")

        self.session.delete(document)
        self.session.commit()
        return True
