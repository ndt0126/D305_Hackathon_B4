"""LLM client implementations.

- OpenAIClient: real calls to the OpenAI Chat Completions API. Each pipeline
  pass is bound to a function-calling tool (app/llm/tools.py) selected from
  the prompt's "TASK:" marker, so the API enforces the output schema.
- get_llm_client: factory that picks OpenAI or the offline mock based on
  USE_MOCK_LLM (see app/llm/mock_client.py).

Both implement the LLMClient protocol defined in app/core/interfaces.py.
"""

import json
import logging

from openai import OpenAI

from app.config import Settings
from app.core.interfaces import LLMClient
from app.llm.mock_client import MockLLMClient
from app.llm.prompts import extract_task, get_system_prompt
from app.llm.tools import TOOLS_BY_TASK

log = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM call fails or returns unusable output."""


class OpenAIClient:
    def __init__(self, settings: Settings):
        self._client = OpenAI(api_key=settings.openai_api_key)
        self._model = settings.openai_model
        self._system_prompt = get_system_prompt(settings.system_prompt_file)

    def complete_json(self, user_prompt: str) -> dict:
        # Known tasks go through a forced tool call (schema-validated by the
        # API); anything else falls back to plain JSON mode.
        tool = TOOLS_BY_TASK.get(extract_task(user_prompt))
        try:
            if tool is not None:
                return self._complete_via_tool(user_prompt, tool)
            return self._complete_via_json_mode(user_prompt)
        except LLMError:
            raise
        except json.JSONDecodeError as exc:
            raise LLMError(f"Model did not return valid JSON: {exc}") from exc
        except Exception as exc:  # network errors, auth errors, rate limits, ...
            raise LLMError(f"OpenAI call failed: {exc}") from exc

    def _complete_via_tool(self, user_prompt: str, tool: dict) -> dict:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=0,
            messages=self._messages(user_prompt),
            tools=[tool],
            tool_choice={"type": "function", "function": {"name": tool["function"]["name"]}},
        )
        calls = response.choices[0].message.tool_calls
        if not calls:
            raise LLMError("Model returned no tool call despite forced tool_choice.")
        return json.loads(calls[0].function.arguments)

    def _complete_via_json_mode(self, user_prompt: str) -> dict:
        response = self._client.chat.completions.create(
            model=self._model,
            temperature=0,
            response_format={"type": "json_object"},
            messages=self._messages(user_prompt),
        )
        return json.loads(response.choices[0].message.content or "")

    def _messages(self, user_prompt: str) -> list[dict]:
        return [
            {"role": "system", "content": self._system_prompt},
            {"role": "user", "content": user_prompt},
        ]


def get_llm_client(settings: Settings) -> LLMClient:
    if settings.use_mock_llm:
        log.info("USE_MOCK_LLM=true -> using deterministic mock LLM")
        return MockLLMClient()
    return OpenAIClient(settings)
