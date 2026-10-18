# ReAct Agent from Scratch

A small Python project to understand **Agentic AI fundamentals** by implementing a ReAct (Reason + Act) agent without an agent framework.

The project uses a local LLM through Ollama and demonstrates how an agent reasons about a task, selects tools, observes their results, and produces a final answer.

## Features

- **ReAct loop:** Implements the Thought → Action → Observation cycle.
- **Local LLM:** Uses Llama 3.2 through Ollama's OpenAI-compatible API.
- **Tools:** Safe arithmetic calculator and dog-weight lookup.
- **Testing:** Unit tests and optional Ollama integration tests.
- **Learning-oriented:** Keeps the agent logic explicit to make the underlying concepts easier to understand.

## How It Works

1. The user submits a question.
2. The LLM decides whether to use a tool.
3. The agent executes the selected tool.
4. The tool result is added as an observation.
5. The LLM continues until it produces a final answer or the agent reaches its iteration limit.

```text
User Question
     |
     v
    LLM
     |
     v
 Parse Action ---> Execute Tool
                       |
                       v
                   Observation
                       |
                       v
                      LLM
                       |
                       v
                  Final Answer
```

## Tech Stack

- Python 3.13+
- Ollama + Llama 3.2
- OpenAI Python SDK
- pytest

## Project Structure

```text
app/
├── agent.py             # ReAct execution loop
├── llm.py               # LLM client
├── prompts.py            # Agent instructions
├── main.py               # Application entry point
└── tools/
    ├── calculator.py     # Safe arithmetic operations
    └── dogs.py           # Example dog-weight lookup
tests/                    # Unit and integration tests
.env.example              # Configuration template
requirements.txt           # Python dependencies
```

## Getting Started

### Prerequisites

- Python 3.13+
- [Ollama](https://ollama.com/) installed and running

Download the model:

```bash
ollama pull llama3.2
```

### Installation

Clone the repository and enter the project directory:

```bash
git clone <your-repository-url>
cd react-agent
```

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Create your local configuration:

```bash
cp .env.example .env
```

Ensure `.env` contains the appropriate Ollama settings:

```env
OPENAI_API_KEY=ollama
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.2:latest
```

These settings target a local Ollama instance; no OpenAI API key is required.

### Run the Agent

```bash
python -m app.main
```

## Testing

Run unit tests:

```bash
python -m pytest
```

Run Ollama integration tests:

```bash
python -m pytest tests/test_ollama_integration.py -v -m integration
```

Integration tests require Ollama to be running with the configured model available.

## Current Limitations

- Tool selection relies on parsing the LLM's text output.
- The agent supports a small set of predefined tools.
- The dog weights are illustrative sample data, not veterinary reference values.
- Local model responses may vary between runs.

## What's Next?

- Improve action parsing and validation.
- Add more tools and error-handling scenarios.
- Reimplement the workflow using **LangGraph** and compare both approaches.

## Learning Goal

Understand the mechanics of a tool-using LLM agent before introducing an orchestration framework.

