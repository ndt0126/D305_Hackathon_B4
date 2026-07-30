"""Interfaces the core logic depends on.

Core modules never import OpenAI, FastAPI or HTTP libraries directly.
Concrete implementations live in app/llm/ and are injected, so the whole
pipeline can run offline (mock) and be exercised from the CLI or tests.
"""

from typing import Protocol


class LLMClient(Protocol):
    def complete_json(self, user_prompt: str) -> dict:
        """Send one prompt, return the model's answer parsed as a JSON object."""
        ...
