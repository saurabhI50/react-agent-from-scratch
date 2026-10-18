
import pytest

from app.llm import get_completion
from app.agent import query


@pytest.mark.integration
def test_ollama_returns_non_empty_response():
    messages = [
        {
            "role": "user",
            "content": "Reply with exactly the word READY.",
        }
    ]

    response = get_completion(messages)

    assert isinstance(response, str)
    assert response.strip()


@pytest.mark.integration
def test_ollama_react_agent_answers_average_weight_question():
    answer = query(
        "What is the arithmetic mean of the average weights "
        "of a Scottish Terrier and a Border Collie? "
        "Use the available tools to look up both weights "
        "and calculate the result."
    )

    assert answer.strip()
    assert "29.5" in answer
