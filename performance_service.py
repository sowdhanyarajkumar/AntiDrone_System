from typing import List, Dict, Any, Optional
from app.database.database import SessionLocal
from app.database.repositories import SystemRepository


class PerformanceService:
    @staticmethod
    def get_latest_computer_metrics(session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            record = repo.get_latest_computer_metrics(session_id)
            if not record:
                return None
            return {
                "id": record.id,
                "session_id": record.session_id,
                "timestamp": record.timestamp.isoformat() + "Z",
                "cpu_usage": record.cpu_usage,
                "ram_usage": record.ram_usage,
                "cpu_temperature": record.cpu_temperature,
                "ai_latency": record.ai_latency,
                "fps": record.fps
            }

    @staticmethod
    def get_computer_history(session_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            records = repo.get_computer_history(session_id, limit)
            return [
                {
                    "id": r.id,
                    "session_id": r.session_id,
                    "timestamp": r.timestamp.isoformat() + "Z",
                    "cpu_usage": r.cpu_usage,
                    "ram_usage": r.ram_usage,
                    "cpu_temperature": r.cpu_temperature,
                    "ai_latency": r.ai_latency,
                    "fps": r.fps
                }
                for r in reversed(records)
            ]
