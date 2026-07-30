"""Assemble the final ToolReport from validated standups and team summary.

Deterministic finishing rules applied here:
- word cap per field/item (settings.max_summary_words);
- secret redaction on every output text (app/core/redact.py);
- agreed empty-state texts instead of invented content.
"""

from datetime import datetime, timezone

from app.config import Settings
from app.core.redact import redact
from app.core.standup import MemberStandup
from app.core.summary import BUCKETS, SummaryItem, TeamSummary
from app.schemas.messages import Bundle
from app.schemas.report import (
    NO_MEMBER_SIGNAL,
    NO_TEAM_SIGNAL,
    DailyEntry,
    ReportMeta,
    ReportSources,
    ReportStats,
    ToolReport,
    WeeklySummary,
)


def _cap(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) > max_words:
        return " ".join(words[:max_words]) + " ..."
    return text


def _clean(text: str, settings: Settings) -> str:
    return redact(_cap(text, settings.max_summary_words))


def _bucket_text(items: list[SummaryItem], settings: Settings) -> str:
    if not items:
        return NO_TEAM_SIGNAL
    return "\n".join(f"- {_clean(item.text, settings)}" for item in items)


def build_report(
    bundle: Bundle,
    standups: list[MemberStandup],
    summary: TeamSummary,
    dropped_evidence_ids: int,
    settings: Settings,
) -> ToolReport:
    dailies = [
        DailyEntry(
            target_discord_id=s.member.target_id,
            yesterday=_clean(s.yesterday, settings) if s.yesterday else NO_MEMBER_SIGNAL,
            today=_clean(s.today, settings) if s.today else NO_MEMBER_SIGNAL,
        )
        for s in standups
    ]

    weekly = WeeklySummary(
        **{bucket: _bucket_text(getattr(summary, bucket), settings) for bucket in BUCKETS}
    )

    sources = ReportSources(
        # Keyed the same way as dailies[].target_discord_id.
        dailies={s.member.target_id: s.evidence_message_ids for s in standups},
        weekly={
            bucket: sorted(
                {mid for item in getattr(summary, bucket) for mid in item.evidence_message_ids}
            )
            for bucket in BUCKETS
        },
    )

    return ToolReport(
        dailies=dailies,
        weekly=weekly,
        meta=ReportMeta(
            report_id=f"rpt_{bundle.date}",
            generated_at=datetime.now(timezone.utc),
            date=bundle.date,
            stats=ReportStats(
                message_count=len(bundle.messages),
                member_count=len(dailies),
                dropped_evidence_ids=dropped_evidence_ids,
            ),
            sources=sources,
        ),
    )
