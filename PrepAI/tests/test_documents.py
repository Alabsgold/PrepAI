import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from app.main import app
from app.database import get_session
from app.services import UserService
from app.schemas import UserCreate
from app.models import SourceDocument, GeneratedQuiz, GeneratedQuestion, GeneratedOption

DATABASE_URL = "sqlite:///test.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


def override_get_session():
    with Session(engine) as session:
        yield session


app.dependency_overrides[get_session] = override_get_session

client = TestClient(app)


@pytest.fixture(name="session")
def session_fixture():
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def test_user(session):
    user_create = UserCreate(username="testuser", password="password123")
    user_service = UserService(session)
    return user_service.create_user(user_create)


@pytest.fixture
def auth_headers(test_user):
    response = client.post("/auth/token", data={"username": "testuser", "password": "password123"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@patch("app.tasks.process_document_task.delay")
def test_upload_document(mock_delay, auth_headers):
    files = {"file": ("test.pdf", b"test content", "application/pdf")}
    response = client.post("/documents/upload", headers=auth_headers, files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "test.pdf"
    assert data["status"] == "PENDING"
    mock_delay.assert_called_once()


def test_get_documents(session, test_user, auth_headers):
    doc1 = SourceDocument(original_filename="doc1.pdf", file_path="/fake/path1", status="COMPLETED", owner_id=test_user.id)
    doc2 = SourceDocument(original_filename="doc2.pdf", file_path="/fake/path2", status="COMPLETED", owner_id=test_user.id)
    session.add_all([doc1, doc2])
    session.commit()

    response = client.get("/documents/", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["original_filename"] == "doc1.pdf"


def test_get_document(session, test_user, auth_headers):
    doc = SourceDocument(original_filename="doc1.pdf", file_path="/fake/path1", status="COMPLETED", owner_id=test_user.id)
    session.add(doc)
    session.commit()

    response = client.get(f"/documents/{doc.id}", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["original_filename"] == "doc1.pdf"


def test_get_quiz(session, test_user, auth_headers):
    doc = SourceDocument(original_filename="doc1.pdf", file_path="/fake/path1", status="COMPLETED", owner_id=test_user.id)
    session.add(doc)
    session.commit()

    quiz = GeneratedQuiz(title="Quiz for doc1", source_document_id=doc.id)
    session.add(quiz)
    session.commit()

    question = GeneratedQuestion(question_text="Q1", quiz_id=quiz.id)
    session.add(question)
    session.commit()

    option1 = GeneratedOption(option_text="A", is_correct=True, question_id=question.id)
    option2 = GeneratedOption(option_text="B", is_correct=False, question_id=question.id)
    session.add_all([option1, option2])
    session.commit()

    response = client.get(f"/documents/{doc.id}/quiz", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Quiz for doc1"
    assert len(data["questions"]) == 1
    assert data["questions"][0]["question_text"] == "Q1"
    assert len(data["questions"][0]["options"]) == 2
    assert data["questions"][0]["options"][0]["option_text"] == "A"


def test_delete_document(session, test_user, auth_headers):
    doc = SourceDocument(original_filename="doc1.pdf", file_path="/fake/path1", status="COMPLETED", owner_id=test_user.id)
    session.add(doc)
    session.commit()

    response = client.delete(f"/documents/{doc.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Document deleted successfully"

    response = client.get(f"/documents/{doc.id}", headers=auth_headers)
    assert response.status_code == 404


def test_unauthorized_access(session, auth_headers):
    other_user_create = UserCreate(username="otheruser", password="password123")
    user_service = UserService(session)
    other_user = user_service.create_user(other_user_create)
    doc = SourceDocument(original_filename="other_doc.pdf", file_path="/fake/path3", status="COMPLETED", owner_id=other_user.id)
    session.add(doc)
    session.commit()

    response = client.get(f"/documents/{doc.id}", headers=auth_headers)
    assert response.status_code == 404
