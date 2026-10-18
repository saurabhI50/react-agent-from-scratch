
import re
from collections.abc import Callable

from app.llm import get_completion
from app.prompts import SYSTEM_PROMPT
from app.tools.calculator import calculate
from app.tools.dogs import average_dog_weight


ActionTool = Callable[[str], object]

KNOWN_ACTIONS: dict[str, ActionTool] = {
    "calculate": calculate,
    "average_dog_weight": average_dog_weight,
}

MAX_TOOL_INPUT_LENGTH = 500
MAX_ACTION_RETRIES = 2

ACTION_PATTERN = re.compile(
    r"^Action:\s*(?P<tool>\w+):\s*(?P<input>.*)$",
    re.MULTILINE,
)

def validate_action_response(response: str) -> tuple[bool, str]:
    """Validate the structure of a text-based ReAct response."""

    lines = [line.strip() for line in response.splitlines() if line.strip()]

    action_lines = [
        line for line in lines
        if line.startswith("Action:")
    ]

    # A tool-action response must contain exactly one Action line.
    if len(action_lines) > 1:
        return False, "Multiple Action lines found. Return exactly one Action."

    # Detect tool-looking lines that omit the required Action: prefix.
    known_tool_names = set(KNOWN_ACTIONS)

    for line in lines:
        if any(
            line.startswith(f"{tool_name}:")
            for tool_name in known_tool_names
        ):
            return False, (
                "Malformed tool request. Use the format "
                "'Action: tool_name: tool input'."
            )

    if not action_lines:
        # No action means this may be a final answer.
        return True, ""

    # Validate the single Action line.
    match = ACTION_PATTERN.fullmatch(action_lines[0])

    if match is None:
        return False, "Malformed Action. Use: Action: tool_name: tool input"

    tool_name = match.group("tool")
    tool_input = match.group("input").strip()

    if not tool_input:
        return False, "Tool input cannot be empty."

    if len(tool_input) > MAX_TOOL_INPUT_LENGTH:
        return False, "Tool input is too long."

    if tool_name not in KNOWN_ACTIONS:
        return False, f"Unknown tool: {tool_name}."

    return True, ""

class Agent:
    def __init__(self, max_turns: int = 5):
        if max_turns < 1:
            raise ValueError("max_turns must be at least 1.")

        self.max_turns = max_turns
        self.messages: list[dict[str, str]] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    def __call__(self, question: str) -> str:
        if not question.strip():
            raise ValueError("Question cannot be empty.")

        self.messages.append(
            {"role": "user", "content": question}
        )
        return self.execute()

    def execute(self) -> str:
        for turn in range(self.max_turns):
            # 1. Ask the LLM what to do next.
            try:
                response = get_completion(self.messages)
            except Exception as exc:
                print(f"LLM request failed: {type(exc).__name__}")
                return (
                    "Error: Unable to get a response from the LLM."
                )

            print(f"\nLLM response:\n{response}")

            # 2. Look for a tool action.
            action_match = ACTION_PATTERN.search(response)

            if action_match is None:
                # An action marker that could not be parsed is not
                # treated as a successful final answer.
                if re.search(r"^Action:", response, re.MULTILINE):
                    return "Error: The LLM returned a malformed action."

                answer_match = re.search(
                    r"^Answer:\s*(.*)",
                    response,
                    re.MULTILINE | re.DOTALL,
                )

                answer = (
                    answer_match.group(1).strip()
                    if answer_match
                    else response.strip()
                )

                self.messages.append(
                    {"role": "assistant", "content": response}
                )
                return answer

            tool_name = action_match.group("tool")
            tool_input = action_match.group("input").strip()

            # 3. Store only the first action, not any extra
            # actions or fabricated observations from the response.
            thoughts = [
                line.strip()
                for line in response[:action_match.start()].splitlines()
                if line.strip().startswith("Thought:")
            ]

            action_message = "\n".join(
                thoughts
                + [
                    f"Action: {tool_name}: {tool_input}",
                    "PAUSE",
                ]
            )

            self.messages.append(
                {"role": "assistant", "content": action_message}
            )

            # 4. Validate and execute the requested tool.
            if not tool_input:
                observation = "Error: Tool input cannot be empty."

            elif len(tool_input) > MAX_TOOL_INPUT_LENGTH:
                observation = "Error: Tool input is too long."

            else:
                tool = KNOWN_ACTIONS.get(tool_name)

                if tool is None:
                    observation = (
                        f"Error: Unknown tool '{tool_name}'."
                    )
                else:
                    try:
                        observation = str(tool(tool_input))
                    except Exception as exc:
                        observation = (
                            f"Tool error: {type(exc).__name__}: {exc}"
                        )

            # 5. The Python tool result is the authoritative observation.
            print(f"Observation: {observation}")

            self.messages.append(
                {
                    "role": "user",
                    "content": f"Observation: {observation}",
                }
            )

        return (
            f"Stopped after {self.max_turns} turns without "
            "receiving a final answer."
        )


def query(question: str, max_turns: int = 5) -> str:
    agent = Agent(max_turns=max_turns)
    return agent(question)
