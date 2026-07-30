"""HTTP routes.

Two ways to feed the pipeline:
1. POST /api/v1/reports/generate
   Push mode — the Discord tool POSTs the exported messages and receives the
   report payload in its own contract (dailies + weekly + meta) in the same
   response. This is the main integration path (tool -> brain -> tool).
2. POST /api/v1/reports/generate-from-export
   Pull mode — this service fetches the bundle from the coworker's export
   API for a given date. PLACEHOLDER until the confidential endpoint is
   provided (see app/integrations/discord_export.py).
"""

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, model_validator

from app.api.security import verify_api_key
from app.config import Settings, get_settings
from app.core.pipeline import generate_report
from app.integrations.discord_export import fetch_bundle
from app.llm.client import get_llm_client
from app.schemas.messages import Bundle
from app.schemas.report import ToolReport

log = logging.getLogger(__name__)
router = APIRouter()


class GenerateReportRequest(BaseModel):
    bundle: Bundle

    @model_validator(mode="before")
    @classmethod
    def accept_unwrapped_payload(cls, data: Any) -> Any:
        """Accept the payload with or without the {"bundle": ...} wrapper.

        A bare message array, {"messages": [...]}, {"data": [...]} and a full
        Bundle object all work — see app/schemas/messages.py for the shapes
        normalized one level down.
        """
        if isinstance(data, list):
            return {"bundle": data}
        if isinstance(data, dict) and "bundle" not in data:
            return {"bundle": data}
        return data


class GenerateFromExportRequest(BaseModel):
    # Day to export and report on, formatted YYYY-MM-DD.
    date: str


@router.get("/health")
def health() -> dict:
    return {"status": "ok"}


@router.get("/api/v1/reports/generate", include_in_schema=False)
def generate_wrong_method() -> None:
    """Answer the common mistake of pointing a liveness check here."""
    raise HTTPException(
        status_code=405,
        detail="This endpoint accepts POST only. For a liveness check use GET /health.",
    )


@router.post(
    "/api/v1/reports/generate",
    response_model=ToolReport,
    dependencies=[Depends(verify_api_key)],
)
def generate(req: GenerateReportRequest, settings: Settings = Depends(get_settings)) -> ToolReport:
    return generate_report(req.bundle, get_llm_client(settings), settings)


@router.post(
    "/api/v1/reports/generate-from-export",
    response_model=ToolReport,
    dependencies=[Depends(verify_api_key)],
)
def generate_from_export(
    req: GenerateFromExportRequest, settings: Settings = Depends(get_settings)
) -> ToolReport:
    # PLACEHOLDER: depends on the confidential export endpoint being configured.
    raw = fetch_bundle(req.date, settings)
    bundle = Bundle.model_validate(raw)
    return generate_report(bundle, get_llm_client(settings), settings)
