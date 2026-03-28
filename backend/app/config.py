from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_BACKEND_DIR = Path(__file__).resolve().parent.parent
_PROJECT_ROOT = _BACKEND_DIR.parent
_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables with SE_ prefix."""

    model_config = SettingsConfigDict(
        env_file=str(_ENV_FILE) if _ENV_FILE.exists() else ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="SE_",
        extra="ignore",
    )

    # ─── Database ───────────────────────────────────────────────
    database_url: str = "postgresql+asyncpg://localhost:5432/salesedge"
    redis_url: str = "redis://localhost:6379/0"

    # ─── Government APIs (Tier 1) ───────────────────────────────
    ogd_api_key: str = ""

    # ─── Market APIs (Tier 2 — Optional) ───────────────────────
    dhan_access_token: str | None = None
    zerodha_api_key: str | None = None
    zerodha_api_secret: str | None = None
    upstox_api_key: str | None = None
    upstox_api_secret: str | None = None
    angel_api_key: str | None = None
    angel_client_id: str | None = None
    fyers_app_id: str | None = None
    fyers_secret_key: str | None = None
    icici_api_key: str | None = None
    icici_api_secret: str | None = None
    delta_api_key: str | None = None
    delta_api_secret: str | None = None

    # ─── Enrichment APIs (Tier 3 — Optional) ───────────────────
    finnhub_api_key: str | None = None
    twelve_data_api_key: str | None = None
    alpha_vantage_api_key: str | None = None
    polygon_api_key: str | None = None
    fmp_api_key: str | None = None
    stockinsights_token: str | None = None
    coingecko_api_key: str | None = None
    open_exchange_rates_app_id: str | None = None
    exchangerate_host_key: str | None = None

    # ─── CRM ───────────────────────────────────────────────────
    salesforce_client_id: str | None = None
    salesforce_client_secret: str | None = None
    hubspot_api_key: str | None = None

    # ─── LLM / AI Provider ──────────────────────────────────────
    # Supports OpenRouter, OpenAI, or any OpenAI-compatible API
    llm_provider: str = "openrouter"  # "openrouter", "openai", "local", "ollama"
    llm_api_key: str | None = None  # OpenRouter/OpenAI API key
    llm_base_url: str = "https://openrouter.ai/api/v1"  # Override for custom endpoints
    llm_model: str = "google/gemini-2.0-flash-001"  # Default model
    llm_fallback_model: str = "meta-llama/llama-3.3-70b-instruct:free"  # Free fallback
    llm_max_tokens: int = 4096
    llm_temperature: float = 0.3  # Lower for business-critical outputs
    llm_timeout_seconds: int = 30

    # ─── Auth / JWT ────────────────────────────────────────────
    jwt_secret_key: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # ─── App ───────────────────────────────────────────────────
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        raw = self.cors_origins.strip()
        if raw.startswith("["):
            import json
            return json.loads(raw)
        return [o.strip() for o in raw.split(",") if o.strip()]


class FeatureFlags(BaseModel):
    """Feature flags for staged rollout of capabilities."""

    enable_prospect_agent: bool = True
    enable_deal_risk_agent: bool = True
    enable_retention_agent: bool = False
    enable_competitive_agent: bool = False
    enable_crm_integration: bool = False
    enable_email_tracking: bool = False
    enable_linkedin_signals: bool = False
    enable_ogd_auto_discovery: bool = True
    enable_rbi_integration: bool = True
    enable_nse_live_data: bool = False
    enable_paper_trading_mode: bool = True
    enable_websocket_alerts: bool = True
    enable_dark_mode: bool = True
    enable_export_functionality: bool = True


@lru_cache
def get_settings() -> Settings:
    """Return a cached singleton of application settings."""
    return Settings()


@lru_cache
def get_feature_flags() -> FeatureFlags:
    """Return a cached singleton of feature flags."""
    return FeatureFlags()
