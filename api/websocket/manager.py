"""WebSocket connection manager for real-time updates"""

from fastapi import WebSocket
from typing import List, Dict, Any
from datetime import datetime
import json
from common.utils.logger import init_logger

logger = init_logger("websocket-manager")


class ConnectionManager:
    """Manage WebSocket connections and broadcast messages"""

    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.user_connections: Dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket):
        """Accept and register a new WebSocket connection"""
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """Unregister a WebSocket connection"""
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket disconnected. Total: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return

        message["timestamp"] = datetime.utcnow().isoformat() + "Z"
        message_str = json.dumps(message)

        disconnected = []
        for websocket in self.active_connections:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending message: {str(e)}")
                disconnected.append(websocket)

        # Clean up disconnected clients
        for websocket in disconnected:
            self.disconnect(websocket)

    async def send_to_user(self, user_id: int, message: Dict[str, Any]):
        """Send message to specific user"""
        message["timestamp"] = datetime.utcnow().isoformat() + "Z"
        message_str = json.dumps(message)

        if user_id not in self.user_connections:
            return

        disconnected = []
        for websocket in self.user_connections[user_id]:
            try:
                await websocket.send_text(message_str)
            except Exception as e:
                logger.error(f"Error sending to user {user_id}: {str(e)}")
                disconnected.append(websocket)

        for websocket in disconnected:
            self.user_connections[user_id].remove(websocket)


# Event types for WebSocket messages
class EventType:
    """Event types for WebSocket messaging"""
    SIGNAL_GENERATED = "signal_generated"
    TRADE_EXECUTED = "trade_executed"
    PRICE_UPDATE = "price_update"
    PORTFOLIO_UPDATE = "portfolio_update"
    ORDER_STATUS = "order_status"
    POSITION_UPDATE = "position_update"
    ERROR = "error"
    HEARTBEAT = "heartbeat"


def create_event(event_type: str, data: Dict[str, Any], user_id: int = None) -> Dict[str, Any]:
    """Create a WebSocket event"""
    return {
        "type": event_type,
        "data": data,
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
    }
