import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_session
from app.services import UserService
from app.schemas import UserCreate

DATABASE_URL = "sqlite:///test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_and_teardown_database():
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


def test_login_for_access_token():
    # Create a user first
    user_create = UserCreate(username="testuser", password="password123")
    user_service = UserService(session=next(override_get_session()))
    user_service.create_user(user_create)

    # Attempt to log in
    response = client.post("/auth/token", data={"username": "testuser", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_for_access_token_incorrect_password():
    # Create a user first
    user_create = UserCreate(username="testuser", password="password123")
    user_service = UserService(session=next(override_get_session()))
    user_service.create_user(user_create)

    # Attempt to log in with incorrect password
    response = client.post("/auth/token", data={"username": "testuser", "password": "wrongpassword"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"