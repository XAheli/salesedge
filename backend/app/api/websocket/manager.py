"""WebSocket connection manager for real-time updates."""
from __future__ import annotations

import asyncio
import json
from datetime import datetime
from typing import Any

from fastapi import WebSocket
import structlog

logger = structlog.get_logger(__name__)


class ConnectionManager:
    """Manages active WebSocket connections and broadcasts."""

    def __init__(self) -> None:
        self._connections: dict[str, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, channel: str = "default") -> None:
        await websocket.accept()
        self._connections.setdefault(channel, []).append(websocket)
        logger.info("ws.connected", channel=channel, total=len(self._connections[channel]))

    def disconnect(self, websocket: WebSocket, channel: str = "default") -> None:
        if channel in self._connections:
            self._connections[channel] = [c for c in self._connections[channel] if c != websocket]
            logger.info("ws.disconnected", channel=channel, total=len(self._connections[channel]))

    async def broadcast(self, channel: str, data: dict[str, Any]) -> None:
        message = json.dumps({**data, "timestamp": datetime.utcnow().isoformat()})
        dead: list[WebSocket] = []
        for ws in self._connections.get(channel, []):
            try:
                await ws.send_text(message)
            except Exception:
                dead.append(ws)
        for ws in dead:
            self.disconnect(ws, channel)

    async def send_personal(self, websocket: WebSocket, data: dict[str, Any]) -> None:
        try:
            await websocket.send_text(json.dumps({**data, "timestamp": datetime.utcnow().isoformat()}))
        except Exception:
            pass

    @property
    def connection_count(self) -> dict[str, int]:
        return {ch: len(conns) for ch, conns in self._connections.items()}


manager = ConnectionManager()
