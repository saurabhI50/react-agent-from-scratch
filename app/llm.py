
import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = os.getenv("OPENAI_MODEL", "llama3.2:latest")

client = OpenAI()

def get_completion(messages: list[dict[str, str]]) -> str:
    """Send conversation messages to the LLM and return its response."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=0,
    )

    content = response.choices[0].message.content

    if not content:
        raise RuntimeError("The LLM returned an empty response.")

    return content.strip()