
from unittest.mock import Mock, patch

from app.agent import Agent
from app.agent import validate_action_response


def test_agent_executes_tool_and_returns_final_answer():
    # Simulate two LLM responses without calling Ollama.
    responses = [
        "Thought: I need to calculate the sum.\n"
        "Action: calculate: 2 + 3\nPAUSE",

        "Thought: The calculation is complete.\n"
        "Answer: The result is 5.",
    ]

    with patch(
        "app.agent.get_completion",
        side_effect=responses,
    ) as mock_llm:
        agent = Agent()
        result = agent("What is 2 + 3?")

    # Verify the final answer.
    assert result == "The result is 5."

    # The LLM should have been called twice.
    assert mock_llm.call_count == 2

    # Verify that the real tool result was passed back
    # to the LLM as an observation.
    second_call_messages = mock_llm.call_args_list[1].args[0]

    assert any(
        message["content"] == "Observation: 5"
        for message in second_call_messages
    )


def test_agent_handles_unknown_tool():
    responses = [
        "Action: unknown_tool: example\nPAUSE",
        "Thought: The requested tool was unavailable.\n"
        "Answer: I could not execute that tool.",
    ]

    with patch(
        "app.agent.get_completion",
        side_effect=responses,
    ):
        agent = Agent()
        result = agent("Use an unknown tool.")

    assert result == "I could not execute that tool."


def test_agent_stops_at_turn_limit():
    # Every response requests an action, so the agent
    # never receives a final answer within two turns.
    responses = [
        "Action: calculate: 1 + 1\nPAUSE",
        "Action: calculate: 2 + 2\nPAUSE",
    ]

    with patch(
        "app.agent.get_completion",
        side_effect=responses,
    ):
        agent = Agent(max_turns=2)
        result = agent("Keep calculating.")

    assert "Stopped after 2 turns" in result


def test_validator_accepts_one_valid_action():
    response = (
        "Thought: Look up the breed.\n"
        "Action: average_dog_weight: Scottish Terrier\n"
        "PAUSE"
    )

    valid, error = validate_action_response(response)

    assert valid is True
    assert error == ""


def test_validator_rejects_multiple_actions():
    response = (
        "Thought: Look up both breeds.\n"
        "Action: average_dog_weight: Scottish Terrier\n"
        "Action: average_dog_weight: Border Collie\n"
        "PAUSE"
    )

    valid, error = validate_action_response(response)

    assert valid is False
    assert "Multiple Action lines" in error


def test_validator_rejects_tool_line_without_action_prefix():
    response = (
        "Thought: Look up both breeds.\n"
        "Action: average_dog_weight: Scottish Terrier\n"
        "average_dog_weight: Border Collie\n"
        "PAUSE"
    )

    valid, error = validate_action_response(response)

    assert valid is False
    assert "Malformed tool request" in error


def test_validator_rejects_unknown_tool():
    response = "Action: unknown_tool: some input\nPAUSE"

    valid, error = validate_action_response(response)

    assert valid is False
    assert "Unknown tool" in error


def test_validator_rejects_empty_tool_input():
    response = "Action: calculate:   \nPAUSE"

    valid, error = validate_action_response(response)

    assert valid is False
    assert "empty" in error.lower()


def test_validator_accepts_final_answer():
    response = (
        "Thought: I have enough information.\n"
        "Answer: The average is 29.5 lbs."
    )

    valid, error = validate_action_response(response)

    assert valid is True
    assert error == ""


def test_agent_executes_only_first_action_in_response():
    responses = [
        (
            "Thought: Look up both breeds.\n"
            "Action: average_dog_weight: Scottish Terrier\n"
            "average_dog_weight: Border Collie\n"
            "PAUSE"
        ),
        "Answer: The lookup is complete.",
    ]

    dog_tool = Mock(return_value="Scottish Terrier weighs 22 lbs.")

    with patch("app.agent.get_completion", side_effect=responses):
        with patch.dict(
            "app.agent.KNOWN_ACTIONS",
            {"average_dog_weight": dog_tool},
        ):
            agent = Agent()
            answer = agent("Look up both breeds.")

    assert answer == "The lookup is complete."
    dog_tool.assert_called_once_with("Scottish Terrier")
