"""Admin and configuration endpoints."""
from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Body

from app.config import get_settings, get_feature_flags
from app.schemas.common import APIResponse

router = APIRouter()


@router.get("/config", response_model=APIResponse[dict])
async def get_app_config() -> APIResponse[dict]:
    settings = get_settings()
    flags = get_feature_flags()
    return APIResponse(data={
        "environment": settings.environment,
        "debug": settings.debug,
        "version": "1.0.0",
        "feature_flags": flags.model_dump(),
        "configured_apis": {
            "ogd": bool(settings.ogd_api_key),
            "llm": bool(settings.llm_api_key),
            "finnhub": bool(settings.finnhub_api_key),
            "alpha_vantage": bool(settings.alpha_vantage_api_key),
        },
    })


@router.get("/stats", response_model=APIResponse[dict])
async def get_system_stats() -> APIResponse[dict]:
    return APIResponse(data={
        "status": "operational",
        "version": "1.0.0",
    })


@router.post("/settings", response_model=APIResponse[dict])
async def save_settings(
    settings_data: dict = Body(...),
) -> APIResponse[dict]:
    return APIResponse(data={
        "status": "saved",
        "timestamp": datetime.utcnow().isoformat(),
    })
