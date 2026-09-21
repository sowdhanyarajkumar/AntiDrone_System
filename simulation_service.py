"""
Simulation Service orchestrating simulation engine ticks, health evaluation,
database persistence, and real-time WebSocket distribution.
Project: SIH PS 26050 - High Altitude Anti-Drone System (DRDO)
"""

import asyncio
from typing import Dict, Any, Optional
from app.simulation.engine import SimulationEngine
from app.services.health_service import HealthEngine
from app.ai.tracker import SoftwareTracker
from app.database.database import SessionLocal
from app.database.repositories import SystemRepository
from app.services.session_service import SessionService
from app.services.event_service import EventService
from app.core.websocket_manager import ws_manager
from app.core.config import settings


class SimulationService:
    def __init__(self):
        self.engine = SimulationEngine(
            tick_seconds=settings.SIM_TICK_SECONDS,
            default_altitude=settings.DEFAULT_ALTITUDE_METERS
        )
        self.health_engine = HealthEngine()
        self.tracker = SoftwareTracker()
        
        self.current_session_id: Optional[str] = None
        self.current_state: Dict[str, Any] = {}
        self.last_health_status = "NORMAL"

        # Wire callbacks
        self.engine.register_tick_callback(self._handle_tick)
        self.engine.register_event_callback(self._handle_engine_event)

    def _handle_engine_event(self, severity: str, event_type: str, message: str):
        if self.current_session_id:
            EventService.record_event(self.current_session_id, severity, event_type, message)

    def _handle_tick(self, state: Dict[str, Any]):
        """Executed every simulation tick."""
        session_id = self.current_session_id
        if not session_id or not self.engine.is_running or self.engine.is_paused:
            return

        env = state["environment"]
        comp = state["computer"]
        track = state["tracking"]

        # Evaluate health
        health = self.health_engine.evaluate(env, comp, track)

        # Check for health status transition to generate event
        if health["status"] != self.last_health_status:
            severity = "CRITICAL" if health["status"] == "CRITICAL" else ("WARNING" if health["status"] in ["WARNING", "DEGRADED"] else "INFO")
            reason_text = health["reasons"][0] if health["reasons"] else f"System health transitioned to {health['status']}"
            EventService.record_event(
                session_id=session_id,
                severity=severity,
                event_type="HEALTH",
                message=f"Health Status: {health['status']} - {reason_text}"
            )
            self.last_health_status = health["status"]

        # Persist to SQLite
        try:
            with SessionLocal() as db:
                repo = SystemRepository(db)
                repo.add_telemetry(session_id, env)
                repo.add_computer_metrics(session_id, comp)
                repo.add_tracking(session_id, track)
        except Exception as ex:
            print(f"[Simulation] SQLite persist error: {ex}")

        # Assemble full packet
        packet = {
            "type": "telemetry",
            "timestamp": state["timestamp"],
            "session_id": session_id,
            "environment": env,
            "computer": comp,
            "tracking": track,
            "health": health
        }
        self.current_state = packet

        # Broadcast packet to all WebSocket subscribers
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                asyncio.create_task(ws_manager.broadcast(packet))
        except Exception:
            pass

    def start_session(self, initial_altitude: float = 1000.0) -> Dict[str, Any]:
        # Stop existing session if active
        if self.current_session_id:
            self.stop_session()

        session = SessionService.create_new_session(initial_altitude=initial_altitude)
        self.current_session_id = session["session_id"]
        self.engine.start(self.current_session_id)
        self.last_health_status = "NORMAL"

        EventService.record_event(
            session_id=self.current_session_id,
            severity="INFO",
            event_type="SIMULATION",
            message=f"Session {self.current_session_id} started at altitude {initial_altitude}m"
        )
        return session

    def pause_session(self) -> bool:
        if self.current_session_id and self.engine.is_running:
            self.engine.pause()
            SessionService.update_status(self.current_session_id, "PAUSED")
            return True
        return False

    def resume_session(self) -> bool:
        if self.current_session_id and self.engine.is_running and self.engine.is_paused:
            self.engine.resume()
            SessionService.update_status(self.current_session_id, "ACTIVE")
            return True
        return False

    def stop_session(self) -> Optional[Dict[str, Any]]:
        if not self.current_session_id:
            return None
        sid = self.current_session_id
        final_alt = self.engine.env_sim.current_altitude
        self.engine.stop()
        res = SessionService.update_status(sid, "COMPLETED", final_altitude=final_alt)
        EventService.record_event(
            session_id=sid,
            severity="INFO",
            event_type="SIMULATION",
            message=f"Session {sid} completed at final altitude {round(final_alt, 1)}m"
        )
        self.current_session_id = None
        return res

    def reset(self):
        self.stop_session()
        self.engine.reset()
        self.current_state = {}


# Singleton instance
simulation_service = SimulationService()
