from __future__ import annotations

from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.deals import router as deals_router
from app.api.v1.data_provenance import router as data_sources_router
from app.api.v1.health import router as health_router
from app.api.v1.agents import router as agents_router
from app.api.v1.prospects import router as prospects_router
from app.api.v1.signals import router as signals_router
from app.api.v1.retention import router as retention_router
from app.api.v1.competitive import router as competitive_router

v1_router = APIRouter()

v1_router.include_router(auth_router, prefix="/auth", tags=["auth"])
v1_router.include_router(health_router, prefix="/health", tags=["health"])
v1_router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
v1_router.include_router(prospects_router, prefix="/prospects", tags=["prospects"])
v1_router.include_router(deals_router, prefix="/deals", tags=["deals"])
v1_router.include_router(data_sources_router, prefix="/data-sources", tags=["data-sources"])
v1_router.include_router(agents_router)
v1_router.include_router(signals_router, prefix="/signals", tags=["signals"])
v1_router.include_router(retention_router, prefix="/retention", tags=["retention"])
v1_router.include_router(competitive_router, prefix="/competitive", tags=["competitive"])
