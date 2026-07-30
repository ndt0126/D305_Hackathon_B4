"""AI pass 2: team-level summary buckets (done / doing / blocked / questions).

Same grounding rules as the standup pass, enforced in code:
- evidence ids that do not exist in the bundle are dropped;
- an item left without any real evidence is discarded entirely
  (format.py renders an empty bucket as "Không có vấn đề được thảo luận.").
"""

import json
import logging

from pydantic import BaseModel, Field

from app.core.interfaces import LLMClient
from app.llm.prompts import build_summary_prompt
from app.schemas.messages import Bundle

log = logging.getLogger(__name__)

BUCKETS = ("done", "doing", "blocked", "questions")


class SummaryItem(BaseModel):
    text: str
    evidence_message_ids: list[str]


class TeamSummary(BaseModel):
    done: list[SummaryItem] = Field(default_factory=list)
    doing: list[SummaryItem] = Field(default_factory=list)
    blocked: list[SummaryItem] = Field(default_factory=list)
    questions: list[SummaryItem] = Field(default_factory=list)


def build_team_summary(bundle: Bundle, llm: LLMClient) -> tuple[TeamSummary, int]:
    """Returns (validated team summary, dropped_evidence_ids)."""
    payload = {
        "messages": [
            {
                "message_id": m.message_id,
                "author": m.author_name,
                "timestamp": m.timestamp.isoformat(),
                "content": m.content,
            }
            for m in bundle.messages
        ]
    }
    raw = llm.complete_json(build_summary_prompt(json.dumps(payload, ensure_ascii=False)))

    known_ids = {m.message_id for m in bundle.messages}
    dropped_ids = 0
    validated: dict[str, list[SummaryItem]] = {}
    for bucket in BUCKETS:
        items: list[SummaryItem] = []
        for item in raw.get(bucket, []):
            text = str(item.get("text", "")).strip()
            claimed = [str(i) for i in item.get("evidence_message_ids", [])]
            evidence = [i for i in claimed if i in known_ids]
            dropped_ids += len(claimed) - len(evidence)
            if not text:
                continue
            if not evidence:
                # No traceable evidence -> the item must not appear.
                log.warning("Summary item without valid evidence dropped: %r", text[:60])
                continue
            items.append(SummaryItem(text=text, evidence_message_ids=evidence))
        validated[bucket] = items

    summary = TeamSummary(**validated)
    log.info(
        "Team summary: %s (%d hallucinated ids dropped)",
        {b: len(getattr(summary, b)) for b in BUCKETS},
        dropped_ids,
    )
    return summary, dropped_ids
