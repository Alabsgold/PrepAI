from fastapi import Depends, HTTPException
from sqlmodel import Session, select
from passlib.context import CryptContext

from .database import get_session
from .models import User
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