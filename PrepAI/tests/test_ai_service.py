import pytest
from unittest.mock import patch, MagicMock
from app.ai_service import generate_quiz_questions_from_text


@patch("app.ai_service.client")
def test_generate_quiz_questions_from_text(mock_openai_client):
    # Mock the OpenAI client's response
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = """
    {
        "questions": [
            {
                "question_text": "What is the capital of France?",
                "options": ["Paris", "London", "Berlin", "Madrid"],
                "correct_answer": "Paris"
            }
        ]
    }
    """
    mock_openai_client.chat.completions.create.return_value = mock_response

    # Call the function with some dummy text
    test_text = "This is a test text."
    questions = generate_quiz_questions_from_text(test_text)

    # Assertions
    assert len(questions) == 1
    assert questions[0]["question_text"] == "What is the capital of France?"
    assert questions[0]["correct_answer"] == "Paris"
    mock_openai_client.chat.completions.create.assert_called_once()