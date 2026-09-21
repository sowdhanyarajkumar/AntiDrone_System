from fastapi import APIRouter
from app.services.simulation_service import simulation_service
from app.core.config import settings

router = APIRouter()


@router.get("/health")
def get_health():
    """Basic service health check."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.PROJECT_VERSION
    }


@router.get("/system/status")
def get_system_status():
    """Detailed operational status of system, simulator, and active session."""
    active_session = simulation_service.current_session_id
    is_running = simulation_service.engine.is_running
    is_paused = simulation_service.engine.is_paused
    
    current_state = simulation_service.current_state
    health = current_state.get("health", {
        "status": "NORMAL",
        "score": 100,
        "reasons": ["System standby — ready for mission session"]
    })

    return {
        "system": "ONLINE",
        "session_id": active_session or "WAITING FOR SESSION",
        "is_simulating": is_running and not is_paused,
        "is_paused": is_paused,
        "mode": "SIMULATION",
        "ai_mode": "LIVE_AI" if getattr(simulation_service, "camera_active", False) else "SIMULATED",
        "altitude": simulation_service.engine.env_sim.current_altitude,
        "health": health
    }
