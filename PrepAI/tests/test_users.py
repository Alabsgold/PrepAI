import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_session

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


def test_create_user():
    response = client.post("/users/", json={"username": "testuser", "password": "password123"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "testuser"
    assert "id" in data


def test_create_user_duplicate_username():
    client.post("/users/", json={"username": "testuser", "password": "password123"})
    response = client.post("/users/", json={"username": "testuser", "password": "password123"})
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already registered"