from fastapi import APIRouter, Query
from typing import Optional
from app.services.telemetry_service import TelemetryService
from app.services.performance_service import PerformanceService

router = APIRouter()


@router.get("/telemetry/latest")
def get_latest_telemetry(session_id: Optional[str] = Query(None)):
    data = TelemetryService.get_latest(session_id)
    return data or {"message": "No telemetry data available yet"}


@router.get("/telemetry/history")
def get_telemetry_history(
    session_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    return TelemetryService.get_history(session_id, limit)


@router.get("/computer/latest")
def get_latest_computer_metrics(session_id: Optional[str] = Query(None)):
    data = PerformanceService.get_latest_computer_metrics(session_id)
    return data or {"message": "No computer metrics available yet"}


@router.get("/computer/history")
def get_computer_history(
    session_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    return PerformanceService.get_computer_history(session_id, limit)
