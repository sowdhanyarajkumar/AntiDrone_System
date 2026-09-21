from typing import List, Dict, Any, Optional
from app.database.database import SessionLocal
from app.database.repositories import SystemRepository


class TelemetryService:
    @staticmethod
    def get_latest(session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            record = repo.get_latest_telemetry(session_id)
            if not record:
                return None
            return {
                "id": record.id,
                "session_id": record.session_id,
                "timestamp": record.timestamp.isoformat() + "Z",
                "altitude": record.altitude,
                "temperature": record.temperature,
                "pressure": record.pressure,
                "humidity": record.humidity,
                "vibration": record.vibration,
                "air_density": record.air_density,
                "cooling_effectiveness": record.cooling_effectiveness
            }

    @staticmethod
    def get_history(session_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            records = repo.get_telemetry_history(session_id, limit)
            # return in chronological order
            return [
                {
                    "id": r.id,
                    "session_id": r.session_id,
                    "timestamp": r.timestamp.isoformat() + "Z",
                    "altitude": r.altitude,
                    "temperature": r.temperature,
                    "pressure": r.pressure,
                    "humidity": r.humidity,
                    "vibration": r.vibration,
                    "air_density": r.air_density,
                    "cooling_effectiveness": r.cooling_effectiveness
                }
                for r in reversed(records)
            ]
