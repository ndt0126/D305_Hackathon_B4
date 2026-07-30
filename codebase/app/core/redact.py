"""Remove obvious secrets from text before it enters a report.

The system prompt already tells the model to exclude credentials, but report
quotes are verbatim message excerpts — so this is the code-level guarantee
(defense in depth): if someone pasted an API key into the chat, it must never
be copied into the report that gets shared.
"""

import re

SECRET_PATTERNS = [
    # OpenAI-style keys
    re.compile(r"sk-[A-Za-z0-9_\-]{16,}"),
    # GitHub tokens
    re.compile(r"ghp_[A-Za-z0-9]{20,}"),
    # Slack tokens
    re.compile(r"xox[abps]-[A-Za-z0-9\-]{10,}"),
    # Discord bot tokens / JWT-shaped secrets
    re.compile(r"[A-Za-z0-9_\-]{20,}\.[A-Za-z0-9_\-]{5,}\.[A-Za-z0-9_\-]{20,}"),
    # Generic "api_key: value" / "password=value" assignments
    re.compile(r"(?i)(api[_ -]?key|access[_ -]?token|token|password|secret)\s*[:=]\s*\S+"),
]

REPLACEMENT = "[REDACTED]"


def redact(text: str) -> str:
    for pattern in SECRET_PATTERNS:
        text = pattern.sub(REPLACEMENT, text)
    return text
