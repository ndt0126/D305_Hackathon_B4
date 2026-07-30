"""FastAPI application entry point.

Run locally:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI

from app.api.errors import register_error_handlers
from app.api.routes import router
from app.config import get_settings
from app.logging_config import setup_logging

APP_VERSION = "0.8.0"


def create_app() -> FastAPI:
    settings = get_settings()
    setup_logging(settings.log_level)

    app = FastAPI(
        title="Daily Report Assistant API",
        description=(
            "Turns one day of exported Discord messages into a structured "
            "daily report draft for a human to review and send."
        ),
        version=APP_VERSION,
    )
    app.include_router(router)
    register_error_handlers(app)
    return app


app = create_app()
