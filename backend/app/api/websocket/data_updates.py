"""WebSocket endpoint for real-time data freshness updates."""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/data-updates")
async def data_updates_ws(websocket: WebSocket) -> None:
    await manager.connect(websocket, "data-updates")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal(websocket, {"type": "ack", "message": "subscribed to data updates"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, "data-updates")
