"""Bundle preparation: normalize the exported messages before the AI passes."""

import logging

from app.schemas.messages import Bundle

log = logging.getLogger(__name__)


def prepare_bundle(bundle: Bundle) -> Bundle:
    """Sort chronologically, drop duplicate ids, fill derived fields."""
    seen: set[str] = set()
    unique = []
    for msg in sorted(bundle.messages, key=lambda m: m.timestamp):
        if msg.message_id in seen:
            log.warning("Duplicate message id %s dropped", msg.message_id)
            continue
        seen.add(msg.message_id)
        if not msg.channel_id and bundle.channel_id:
            # Export-tool messages carry no channel info; fall back to the
            # bundle-level channel so message links can still be built.
            msg = msg.model_copy(update={"channel_id": bundle.channel_id})
        unique.append(msg)

    # Prefer an explicit date; otherwise use the latest message's UTC date.
    # Callers should pass `date` explicitly when the team timezone matters.
    date = bundle.date or (unique[-1].timestamp.date().isoformat() if unique else "unknown")
    channels = bundle.channels or sorted({m.channel_name for m in unique if m.channel_name})
    return bundle.model_copy(update={"messages": unique, "channels": channels, "date": date})
