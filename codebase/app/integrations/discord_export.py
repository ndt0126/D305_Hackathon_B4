"""Client for the coworker's Discord export tool API.

=== PLACEHOLDER — CONFIDENTIAL ENDPOINT ===
The real endpoint is confidential and still pending. To fill this in, ask
the coworker who runs the export tool for exactly four things:
  1. Base URL of their service (e.g. http://<their-machine>:<port>/api/export)
     -> put it in DISCORD_EXPORT_API_URL in .env
  2. Auth scheme (header name + key). This client sends
     "Authorization: Bearer <key>" -> put the key in DISCORD_EXPORT_API_KEY
     in .env; adjust the header below if their scheme differs.
  3. Query params for the time range. This client currently sends
     ?date=YYYY-MM-DD&format=json — adjust `params` below if they use
     e.g. from/to timestamps instead.
  4. Confirmation the response is a bare JSON array of
     {id, author, content, timestamp}
     (see data/samples/sample_tool_export_input.json) — the Bundle schema
     accepts it directly. Also ask them to ADD `channel_id` + `guild_id`
     per message so report message links can be built (see README).

Note: if their tool can POST to this service instead (push mode,
/api/v1/reports/generate), nothing here is needed at all.

HARD RULE reminder (project rule #3): only point this at the private
practice server with simulated data. Never export messages from the locked
class Discord server.
"""

import logging

import httpx

from app.config import Settings

log = logging.getLogger(__name__)


class ExportAPIError(Exception):
    """Raised when the Discord export API cannot deliver a bundle."""


def fetch_bundle(date: str, settings: Settings) -> dict:
    """Fetch one day of exported messages as a raw dict (Bundle-shaped).

    Args:
        date: day to export, formatted YYYY-MM-DD.
    """
    # PLACEHOLDER: adjust params/headers/path to the real API contract.
    try:
        response = httpx.get(
            settings.discord_export_api_url,
            params={"date": date, "format": "json"},
            headers={"Authorization": f"Bearer {settings.discord_export_api_key}"},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPError as exc:
        log.error("Discord export API call failed: %s", exc)
        raise ExportAPIError(f"Discord export API call failed: {exc}") from exc
