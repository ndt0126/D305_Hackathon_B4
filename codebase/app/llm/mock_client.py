"""Deterministic offline stand-in for the LLM.

Used when USE_MOCK_LLM=true (tests, demos without an API key). The rules are
intentionally simple and explainable — this is NOT meant to be smart:

- standup: a member's messages with "done"-type keywords fill `yesterday`,
  messages with "will/plan"-type keywords fill `today`; nothing matched -> "".
- team_summary: each message lands in the first matching bucket
  (done keyword -> done; blocker keyword -> blocked; ends with "?" ->
  questions; plan keyword -> doing; otherwise skipped).

It parses the "TASK: <name>" / "INPUT:" contract from app/llm/prompts.py.
"""

import json
import re

DONE_RE = re.compile(
    r"\b(done|finished|merged|fixed|completed|resolved|deployed|posted)\b|đã xong|hoàn thành",
    re.IGNORECASE,
)
PLAN_RE = re.compile(r"\b(will|tomorrow|plan|going to)\b|sẽ làm|ngày mai", re.IGNORECASE)
BLOCK_RE = re.compile(
    r"\b(blocked|stuck|error|timeout|timing out|failing|no idea)\b|lỗi|vướng",
    re.IGNORECASE,
)


class MockLLMClient:
    def complete_json(self, user_prompt: str) -> dict:
        task, payload = self._parse(user_prompt)
        if task == "standup":
            return self._standup(payload)
        return self._team_summary(payload)

    @staticmethod
    def _parse(prompt: str) -> tuple[str, dict]:
        task = prompt.splitlines()[0].removeprefix("TASK:").strip()
        payload = json.loads(prompt.split("INPUT:", 1)[1])
        return task, payload

    @staticmethod
    def _standup(payload: dict) -> dict:
        members = []
        for member in payload["members"]:
            done_msgs = [m for m in member["messages"] if DONE_RE.search(m["content"])]
            plan_msgs = [m for m in member["messages"] if PLAN_RE.search(m["content"])]
            evidence = [m["message_id"] for m in done_msgs + plan_msgs]
            members.append(
                {
                    "member_key": member["member_key"],
                    "yesterday": done_msgs[-1]["content"] if done_msgs else "",
                    "today": plan_msgs[-1]["content"] if plan_msgs else "",
                    # Deduplicate while preserving order.
                    "evidence_message_ids": list(dict.fromkeys(evidence)),
                }
            )
        return {"members": members}

    @staticmethod
    def _team_summary(payload: dict) -> dict:
        buckets: dict[str, list[dict]] = {"done": [], "doing": [], "blocked": [], "questions": []}
        for msg in payload["messages"]:
            item = {"text": msg["content"], "evidence_message_ids": [msg["message_id"]]}
            content = msg["content"]
            if DONE_RE.search(content):
                buckets["done"].append(item)
            elif BLOCK_RE.search(content):
                buckets["blocked"].append(item)
            elif content.strip().endswith("?"):
                buckets["questions"].append(item)
            elif PLAN_RE.search(content):
                buckets["doing"].append(item)
        return buckets
