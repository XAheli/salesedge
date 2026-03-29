"""APScheduler-based job scheduler for ingestion connectors.

Supports tiered scheduling:
- Tier 1 (government data): daily
- Tier 2 (market data): every 15 minutes during market hours
- Tier 3 (enrichment): hourly
"""

from __future__ import annotations

from datetime import datetime, time
from typing import Any, Callable, Awaitable

import structlog

try:
    from apscheduler.schedulers.asyncio import AsyncIOScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger

    _APSCHEDULER_AVAILABLE = True
except ImportError:  # pragma: no cover
    _APSCHEDULER_AVAILABLE = False

logger = structlog.get_logger(__name__)

TIER_SCHEDULES: dict[int, dict[str, Any]] = {
    1: {
        "name": "government",
        "trigger_type": "cron",
        "hour": 6,
        "minute": 0,
        "description": "Daily at 06:00 IST",
    },
    2: {
        "name": "market",
        "trigger_type": "interval",
        "minutes": 15,
        "start_time": time(9, 15),
        "end_time": time(15, 30),
        "description": "Every 15 min during NSE/BSE market hours (09:15–15:30 IST)",
    },
    3: {
        "name": "enrichment",
        "trigger_type": "interval",
        "minutes": 60,
        "description": "Hourly",
    },
}

# IST market hours for Tier 2
MARKET_OPEN = time(9, 15)
MARKET_CLOSE = time(15, 30)


class IngestionScheduler:
    """Schedule ingestion jobs with tiered frequency based on connector type."""

    def __init__(self) -> None:
        self._scheduler: Any | None = None
        self._jobs: dict[str, dict[str, Any]] = {}
        self._is_running = False

        if _APSCHEDULER_AVAILABLE:
            self._scheduler = AsyncIOScheduler(timezone="Asia/Kolkata")

    def schedule_connector(
        self,
        connector_name: str,
        tier: int,
        callback: Callable[..., Awaitable[Any]],
        custom_schedule: dict[str, Any] | None = None,
    ) -> None:
        """Register a connector with its tier-appropriate schedule.

        Parameters
        ----------
        connector_name : unique connector identifier
        tier : 1 (government), 2 (market), or 3 (enrichment)
        callback : async callable to invoke on each tick
        custom_schedule : override the default tier schedule
        """
        schedule = custom_schedule or TIER_SCHEDULES.get(tier)
        if not schedule:
            logger.warning(
                "scheduler.unknown_tier",
                connector=connector_name,
                tier=tier,
            )
            return

        if self._scheduler is None:
            logger.warning(
                "scheduler.apscheduler_not_available",
                connector=connector_name,
            )
            self._jobs[connector_name] = {
                "tier": tier,
                "schedule": schedule,
                "status": "pending_no_scheduler",
            }
            return

        trigger = self._build_trigger(schedule)
        job = self._scheduler.add_job(
            callback,
            trigger=trigger,
            id=connector_name,
            name=f"ingest_{connector_name}",
            replace_existing=True,
            kwargs={"connector_name": connector_name},
        )

        self._jobs[connector_name] = {
            "tier": tier,
            "schedule": schedule,
            "job_id": job.id,
            "status": "scheduled",
        }

        logger.info(
            "scheduler.connector_scheduled",
            connector=connector_name,
            tier=tier,
            schedule=schedule.get("description", "custom"),
        )

    def unschedule_connector(self, connector_name: str) -> None:
        """Remove a scheduled connector."""
        if self._scheduler and connector_name in self._jobs:
            try:
                self._scheduler.remove_job(connector_name)
            except Exception:
                pass
        self._jobs.pop(connector_name, None)

    def start(self) -> None:
        """Start the scheduler."""
        if self._scheduler and not self._is_running:
            self._scheduler.start()
            self._is_running = True
            logger.info("scheduler.started", jobs=len(self._jobs))

    def stop(self) -> None:
        """Gracefully shut down the scheduler."""
        if self._scheduler and self._is_running:
            self._scheduler.shutdown(wait=True)
            self._is_running = False
            logger.info("scheduler.stopped")

    def get_status(self) -> dict[str, Any]:
        """Return the current status of all scheduled jobs."""
        return {
            "running": self._is_running,
            "total_jobs": len(self._jobs),
            "jobs": {
                name: {
                    "tier": info["tier"],
                    "description": info["schedule"].get("description", "custom"),
                    "status": info["status"],
                }
                for name, info in self._jobs.items()
            },
        }

    @staticmethod
    def is_market_hours() -> bool:
        """Check if the current time (IST) is within NSE/BSE trading hours."""
        try:
            from zoneinfo import ZoneInfo
        except ImportError:
            from backports.zoneinfo import ZoneInfo  # type: ignore[no-redef]

        now_ist = datetime.now(ZoneInfo("Asia/Kolkata")).time()
        return MARKET_OPEN <= now_ist <= MARKET_CLOSE

    # ── Private ──────────────────────────────────────────────────────────

    @staticmethod
    def _build_trigger(schedule: dict[str, Any]) -> Any:
        if not _APSCHEDULER_AVAILABLE:
            raise RuntimeError("APScheduler is required for trigger creation")

        trigger_type = schedule.get("trigger_type", "interval")

        if trigger_type == "cron":
            return CronTrigger(
                hour=schedule.get("hour", 6),
                minute=schedule.get("minute", 0),
                timezone="Asia/Kolkata",
            )

        start_time = schedule.get("start_time")
        end_time = schedule.get("end_time")
        if start_time and end_time:
            return CronTrigger(
                minute=f"*/{schedule.get('minutes', 15)}",
                hour=f"{start_time.hour}-{end_time.hour}",
                day_of_week="mon-fri",
                timezone="Asia/Kolkata",
            )

        return IntervalTrigger(
            minutes=schedule.get("minutes", 60),
            timezone="Asia/Kolkata",
        )
