"""End-to-end pipeline: Bundle -> ToolReport.

Stages: prepare -> standup (AI pass 1, per member)
        -> team_summary (AI pass 2, whole team)
        -> format (deterministic: caps, redaction, empty-state texts).

The same function serves the API, the CLI and the tests.
"""

import logging

from app.config import Settings
from app.core.bundle import prepare_bundle
from app.core.format import build_report
from app.core.interfaces import LLMClient
from app.core.standup import build_standups
from app.core.summary import build_team_summary
from app.schemas.messages import Bundle
from app.schemas.report import ToolReport

log = logging.getLogger(__name__)


def generate_report(bundle: Bundle, llm: LLMClient, settings: Settings) -> ToolReport:
    bundle = prepare_bundle(bundle)
    log.info("Generating report for %s: %d messages", bundle.date, len(bundle.messages))

    standups, dropped_standup = build_standups(bundle, llm)
    summary, dropped_summary = build_team_summary(bundle, llm)
    report = build_report(bundle, standups, summary, dropped_standup + dropped_summary, settings)

    log.info(
        "Report %s: %d members, weekly buckets %s",
        report.meta.report_id,
        len(report.dailies),
        {b: len(getattr(summary, b)) for b in ("done", "doing", "blocked", "questions")},
    )
    return report
