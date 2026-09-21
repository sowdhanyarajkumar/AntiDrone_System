from fastapi import APIRouter, Query
from typing import Optional, List
from app.services.event_service import EventService
from app.schemas.events import SystemEventResponse

router = APIRouter()


@router.get("/events")
def get_events(
    session_id: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    return EventService.get_recent_events(session_id=session_id, limit=limit)
