"""Inbound API-key check for public deployments.

The service may be exposed to the internet (e.g. via a Cloudflare Tunnel) so
the Discord tool can reach it from anywhere. When SERVICE_API_KEY is set,
every report endpoint requires the same value in the "X-API-Key" header —
share the key privately with the tool's owner, never commit it.
When SERVICE_API_KEY is empty (local development), no auth is enforced.
/health stays open either way so tunnel checks keep working.
"""

from fastapi import Depends, Header, HTTPException

from app.config import Settings, get_settings


def verify_api_key(
    x_api_key: str | None = Header(default=None),
    settings: Settings = Depends(get_settings),
) -> None:
    if settings.service_api_key and x_api_key != settings.service_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header.")
