import uuid
from pathlib import Path
from fastapi import Depends, HTTPException, UploadFile
from sqlmodel import Session, select
from passlib.context import CryptContext

from .database import get_session
from .models import User, SourceDocument
from .schemas import UserCreate
from .tasks import process_document_task

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

        process_document_task.delay(db_document.id)

        return db_document