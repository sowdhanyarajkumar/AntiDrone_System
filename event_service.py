import asyncio
import datetime
from typing import List, Dict, Any, Optional
from app.database.database import SessionLocal
from app.database.repositories import SystemRepository
from app.core.websocket_manager import ws_manager


class EventService:
    @staticmethod
    def record_event(session_id: str, severity: str, event_type: str, message: str) -> Dict[str, Any]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            event = repo.add_event(session_id, severity, event_type, message)
            event_dict = {
                "id": event.id,
                "session_id": event.session_id,
                "timestamp": event.timestamp.isoformat() + "Z",
                "severity": event.severity,
                "event_type": event.event_type,
                "message": event.message
            }

        # Broadcast event over WebSocket
        packet = {
            "type": "event",
            "timestamp": event_dict["timestamp"],
            "session_id": session_id,
            "severity": severity,
            "event_type": event_type,
            "message": message
        }
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(ws_manager.broadcast(packet))
        except Exception:
            pass

        return event_dict

    @staticmethod
    def get_recent_events(session_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            events = repo.get_events(session_id=session_id, limit=limit)
            return [
                {
                    "id": e.id,
                    "session_id": e.session_id,
                    "timestamp": e.timestamp.isoformat() + "Z",
                    "severity": e.severity,
                    "event_type": e.event_type,
                    "message": e.message
                }
                for e in events
            ]
