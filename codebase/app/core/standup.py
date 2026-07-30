"""AI pass 1: per-member standup (yesterday / today) from their own messages.

Members are identified by their Discord id when the export provides one, so
people who share a display name never get merged, and the daily always routes
back to the right account.

The prompt refers to each member by a short opaque `member_key` (m1, m2, ...)
instead of their name. The model only has to echo that key back, which cannot
be mangled the way a display name can ("dquangminh." losing its dot, diacritics
being rewritten) — and an unrecognized key is dropped rather than silently
attributed to the wrong person.

Anti-fabrication rules enforced here in code:
- a member_key the model invents is dropped;
- evidence ids that do not exist in the bundle are dropped;
- a claim left without any real evidence is cleared back to empty
  (format.py renders empty fields as "Không có thông tin.");
- every real author appears in the result, even with no signal.
"""

import json
import logging

from pydantic import BaseModel, Field

from app.core.interfaces import LLMClient
from app.llm.prompts import build_standup_prompt
from app.schemas.messages import Bundle, DiscordMessage

log = logging.getLogger(__name__)


class Member(BaseModel):
    # Opaque key used inside prompts only.
    key: str
    display_name: str
    # What the tool mentions as <@id>: the Discord snowflake, or the display
    # name when the export carries no id for this member.
    target_id: str


class MemberStandup(BaseModel):
    member: Member
    yesterday: str = ""
    today: str = ""
    evidence_message_ids: list[str] = Field(default_factory=list)


def _identity(msg: DiscordMessage) -> str:
    """Prefer the Discord id; fall back to the display name."""
    return msg.author_id or msg.author_name


def collect_members(bundle: Bundle) -> list[Member]:
    """One Member per distinct author, in first-appearance order."""
    members: dict[str, Member] = {}
    for msg in bundle.messages:
        identity = _identity(msg)
        if identity not in members:
            members[identity] = Member(
                key=f"m{len(members) + 1}",
                display_name=msg.author_name,
                target_id=identity,
            )
    return list(members.values())


def build_standups(bundle: Bundle, llm: LLMClient) -> tuple[list[MemberStandup], int]:
    """Returns (one standup per member in first-appearance order, dropped_evidence_ids)."""
    members = collect_members(bundle)
    messages_by_identity: dict[str, list[DiscordMessage]] = {m.target_id: [] for m in members}
    for msg in bundle.messages:
        messages_by_identity[_identity(msg)].append(msg)

    payload = {
        "members": [
            {
                "member_key": member.key,
                "display_name": member.display_name,
                "messages": [
                    {
                        "message_id": m.message_id,
                        "timestamp": m.timestamp.isoformat(),
                        "content": m.content,
                    }
                    for m in messages_by_identity[member.target_id]
                ],
            }
            for member in members
        ]
    }
    raw = llm.complete_json(build_standup_prompt(json.dumps(payload, ensure_ascii=False)))

    known_ids = {m.message_id for m in bundle.messages}
    by_key = {m.key: m for m in members}
    results: dict[str, MemberStandup] = {}
    dropped_ids = 0

    for item in raw.get("members", []):
        key = str(item.get("member_key", ""))
        member = by_key.get(key)
        if member is None:
            log.warning("Standup for unknown member_key %r -> discarded", key)
            continue
        if key in results:
            log.warning("Duplicate standup for %s -> first one kept", member.display_name)
            continue

        claimed = [str(i) for i in item.get("evidence_message_ids", [])]
        evidence = [i for i in claimed if i in known_ids]
        dropped_ids += len(claimed) - len(evidence)

        yesterday = str(item.get("yesterday", ""))
        today = str(item.get("today", ""))
        if (yesterday or today) and not evidence:
            # No traceable evidence -> the claims must not appear.
            log.warning("Standup for %s has no valid evidence -> cleared", member.display_name)
            yesterday, today = "", ""

        results[key] = MemberStandup(
            member=member,
            yesterday=yesterday,
            today=today,
            evidence_message_ids=evidence,
        )

    standups = [results.get(m.key, MemberStandup(member=m)) for m in members]
    log.info(
        "Standups built for %d members (%d hallucinated ids dropped)", len(standups), dropped_ids
    )
    return standups, dropped_ids
