"""WebSocket endpoint for real-time deal risk alerts."""
from __future__ import annotations

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.api.websocket.manager import manager

router = APIRouter()


@router.websocket("/ws/alerts")
async def deal_alerts_ws(websocket: WebSocket) -> None:
    await manager.connect(websocket, "alerts")
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal(websocket, {"type": "ack", "message": "subscribed to alerts"})
    except WebSocketDisconnect:
        manager.disconnect(websocket, "alerts")
