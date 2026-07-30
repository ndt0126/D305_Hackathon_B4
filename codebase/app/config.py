"""Application configuration.

All settings are loaded from environment variables (or a local `.env` file).
See `.env.example` for the full list with explanations.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- OpenAI ---
    openai_api_key: str = "sk-REPLACE_ME"
    openai_model: str = "gpt-4o-mini"
    # Safe default: no external calls until a real key is configured.
    use_mock_llm: bool = True
    # PLACEHOLDER: optional path to a file with the final production prompt.
    system_prompt_file: str | None = None

    # --- Discord export tool API (coworker's service) ---
    # PLACEHOLDER: the real endpoint is confidential; replace via .env.
    discord_export_api_url: str = "https://example.invalid/api/export"
    discord_export_api_key: str = "REPLACE_ME"

    # --- Inbound auth (public deployment) ---
    # When set, report endpoints require this value in the X-API-Key header.
    # Empty (default) disables auth for local development.
    service_api_key: str = ""

    # --- App ---
    log_level: str = "INFO"

    # --- Report constraints (right-sized output) ---
    max_summary_words: int = 25


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance, used as a FastAPI dependency."""
    return Settings()
