from fastapi import APIRouter, Depends
from ..schemas import UserCreate, UserRead
from ..services import UserService

router = APIRouter()


@router.post("/", response_model=UserRead)
def create_user(user_create: UserCreate, user_service: UserService = Depends()):
    return user_service.create_user(user_create)