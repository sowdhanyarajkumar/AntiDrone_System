from fastapi import APIRouter, Query
from typing import Optional
from app.database.database import SessionLocal
from app.database.repositories import SystemRepository
from app.services.simulation_service import simulation_service

router = APIRouter()


@router.get("/tracking/latest")
def get_latest_tracking(session_id: Optional[str] = Query(None)):
    with SessionLocal() as db:
        repo = SystemRepository(db)
        rec = repo.get_latest_tracking(session_id)
        if rec:
            return {
                "id": rec.id,
                "session_id": rec.session_id,
                "timestamp": rec.timestamp.isoformat() + "Z",
                "target_x": rec.target_x,
                "target_y": rec.target_y,
                "image_center_x": rec.image_center_x,
                "image_center_y": rec.image_center_y,
                "error_x": rec.error_x,
                "error_y": rec.error_y,
                "pan_angle": rec.pan_angle,
                "tilt_angle": rec.tilt_angle,
                "confidence": rec.tracking_confidence,
                "status": rec.status
            }
    # Fallback to simulation instantaneous tracking solver
    snap = simulation_service.engine.generate_current_state()
    return snap["tracking"]


@router.get("/tracking/history")
def get_tracking_history(session_id: Optional[str] = Query(None), limit: int = Query(100, ge=1, le=1000)):
    with SessionLocal() as db:
        repo = SystemRepository(db)
        records = repo.get_tracking_history(session_id, limit=limit)
        return [
            {
                "id": r.id,
                "session_id": r.session_id,
                "timestamp": r.timestamp.isoformat() + "Z",
                "target_x": r.target_x,
                "target_y": r.target_y,
                "image_center_x": r.image_center_x,
                "image_center_y": r.image_center_y,
                "error_x": r.error_x,
                "error_y": r.error_y,
                "pan_angle": r.pan_angle,
                "tilt_angle": r.tilt_angle,
                "confidence": r.tracking_confidence,
                "status": r.status
            }
            for r in reversed(records)
        ]
