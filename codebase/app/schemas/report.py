"""Output schemas: the report payload the Discord tool receives.

Contract requested by the tool's owner (2026-07-30):

{
  "dailies": [ {"target_username": ..., "yesterday": ..., "today": ...}, ... ],
  "weekly":  {"done": ..., "doing": ..., "blocked": ..., "questions": ...}
}

`meta` is an EXTRA block for traceability (message-id sources, stats) used by
our eval; the tool can simply ignore it — extra JSON keys do not break
standard parsers.

Anti-fabrication rule (agreed 2026-07-30): when there is no useful work/study
signal, fields say so explicitly instead of being invented:
- an empty weekly bucket        -> "Không có vấn đề được thảo luận."
- a member's missing field      -> "Không có thông tin."
"""

from datetime import datetime

from pydantic import BaseModel, Field

NO_TEAM_SIGNAL = "Không có vấn đề được thảo luận."
NO_MEMBER_SIGNAL = "Không có thông tin."


class DailyEntry(BaseModel):
    # The Discord snowflake the tool mentions as <@id>. Falls back to the
    # author's display name when the export carries no id for that member.
    target_discord_id: str
    yesterday: str = NO_MEMBER_SIGNAL
    today: str = NO_MEMBER_SIGNAL


class WeeklySummary(BaseModel):
    # Multi-item buckets are newline-joined "- item" lines.
    done: str = NO_TEAM_SIGNAL
    doing: str = NO_TEAM_SIGNAL
    blocked: str = NO_TEAM_SIGNAL
    questions: str = NO_TEAM_SIGNAL


class ReportStats(BaseModel):
    message_count: int
    member_count: int
    # Evidence ids returned by the LLM that did not exist in the bundle
    # (hallucination attempts caught and dropped).
    dropped_evidence_ids: int = 0


class ReportSources(BaseModel):
    """Message ids backing each output claim — traceability for eval."""

    dailies: dict[str, list[str]] = Field(default_factory=dict)
    weekly: dict[str, list[str]] = Field(default_factory=dict)


class ReportMeta(BaseModel):
    report_id: str
    generated_at: datetime
    date: str
    stats: ReportStats
    sources: ReportSources


class ToolReport(BaseModel):
    dailies: list[DailyEntry]
    weekly: WeeklySummary
    meta: ReportMeta
