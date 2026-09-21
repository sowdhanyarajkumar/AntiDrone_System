from fastapi import APIRouter, HTTPException, Response
from typing import List, Optional
from app.services.session_service import SessionService

router = APIRouter()


@router.get("/sessions")
def list_sessions():
    return SessionService.get_all_sessions()


@router.get("/sessions/{session_id}")
def get_session_detail(session_id: str):
    sess = SessionService.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
    analytics = SessionService.get_analytics(session_id)
    return {
        "session": sess,
        "analytics": analytics
    }


@router.get("/sessions/{session_id}/export")
def export_session_csv(session_id: str):
    sess = SessionService.get_session(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail=f"Session {session_id} not found")

    csv_data = SessionService.export_csv(session_id)
    filename = f"Aeronex_Telemetry_{session_id}.csv"
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
