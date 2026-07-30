"""Application-wide error handling.

Every handled error becomes a structured JSON body:
    {"error": "<machine_readable_code>", "detail": <...>}
"""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.redact import redact
from app.integrations.discord_export import ExportAPIError
from app.llm.client import LLMError

log = logging.getLogger(__name__)

# How much of a rejected body to log — enough to diagnose, not a full dump.
BODY_LOG_LIMIT = 1500

ACCEPTED_SHAPES_HINT = (
    'Send the messages as a bare JSON array, or wrapped as {"bundle": [...]} / '
    '{"messages": [...]}. Each message needs an id, an author, a content string '
    "and an ISO 8601 timestamp."
)


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        # Log what was actually sent — the fastest way to diagnose a caller
        # whose payload shape we cannot see. Redacted: chat messages may
        # contain pasted credentials.
        raw = (await request.body()).decode("utf-8", errors="replace")
        log.warning(
            "Rejected body on %s (%d bytes): %s",
            request.url.path,
            len(raw),
            redact(raw[:BODY_LOG_LIMIT]),
        )
        # Deliberately drop Pydantic's "input" field: echoing the caller's own
        # payload back made an integration partner think the service was
        # returning their request instead of a report.
        problems = [
            {"field": ".".join(str(p) for p in err.get("loc", [])), "problem": err.get("msg", "")}
            for err in exc.errors()
        ]
        return JSONResponse(
            status_code=422,
            content={
                "error": "invalid_request_body",
                "detail": problems,
                "hint": ACCEPTED_SHAPES_HINT,
            },
        )

    @app.exception_handler(LLMError)
    async def llm_error_handler(request: Request, exc: LLMError) -> JSONResponse:
        log.error("LLM error on %s: %s", request.url.path, exc)
        return JSONResponse(status_code=502, content={"error": "llm_error", "detail": str(exc)})

    @app.exception_handler(ExportAPIError)
    async def export_error_handler(request: Request, exc: ExportAPIError) -> JSONResponse:
        log.error("Export API error on %s: %s", request.url.path, exc)
        return JSONResponse(
            status_code=502, content={"error": "export_api_error", "detail": str(exc)}
        )

    @app.exception_handler(Exception)
    async def unexpected_error_handler(request: Request, exc: Exception) -> JSONResponse:
        log.exception("Unhandled error on %s", request.url.path)
        return JSONResponse(
            status_code=500,
            content={"error": "internal_error", "detail": "Unexpected server error."},
        )
