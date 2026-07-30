"""CLI entry point — runs the exact same pipeline as the API, no server needed.

Used for eval runs and for live demo cases where a judge provides an
arbitrary bundle file (full Bundle object or the export tool's bare array).

Usage (from the codebase/ directory):
    python -m app.cli --input data/samples/sample_bundle_input.json
    python -m app.cli --input bundle.json --output report.json
    python -m app.cli --input bundle.json --mock          # force offline mock
"""

import argparse
import json
import sys
from pathlib import Path

from app.config import Settings
from app.core.pipeline import generate_report
from app.llm.client import get_llm_client
from app.logging_config import setup_logging
from app.schemas.messages import Bundle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a daily report from a bundle file.")
    parser.add_argument("--input", required=True, help="Path to a bundle JSON file")
    parser.add_argument("--output", help="Write the report JSON here (default: stdout)")
    parser.add_argument("--mock", action="store_true", help="Force the offline mock LLM")
    args = parser.parse_args(argv)

    settings = Settings()
    if args.mock:
        settings = settings.model_copy(update={"use_mock_llm": True})
    setup_logging(settings.log_level)

    bundle = Bundle.model_validate_json(Path(args.input).read_text(encoding="utf-8"))
    report = generate_report(bundle, get_llm_client(settings), settings)
    report_json = json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False)

    if args.output:
        Path(args.output).write_text(report_json + "\n", encoding="utf-8")
        print(f"Report written to {args.output}")
    else:
        print(report_json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
