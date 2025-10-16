import pytest
from unittest.mock import patch
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


@pytest.fixture
def authenticated_user_token():
    user_create = UserCreate(username="testuser", password="password123")
    user_service = UserService(session=next(override_get_session()))
    user_service.create_user(user_create)
    response = client.post("/auth/token", data={"username": "testuser", "password": "password123"})
    return response.json()["access_token"]


@patch("app.tasks.process_document_task.delay")
def test_upload_document(mock_delay, authenticated_user_token):
    headers = {"Authorization": f"Bearer {authenticated_user_token}"}
    files = {"file": ("test.pdf", b"test content", "application/pdf")}

    response = client.post("/documents/upload", headers=headers, files=files)

    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "test.pdf"
    assert data["status"] == "PENDING"
    assert "id" in data

    mock_delay.assert_called_once_with(data["id"])