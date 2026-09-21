import csv
import io
import datetime
from typing import List, Dict, Any, Optional
from app.database.database import SessionLocal
from app.database.repositories import SystemRepository
from app.database.models import TelemetryModel, ComputerMetricsModel, DetectionModel, TrackingModel, SystemEventModel


class SessionService:
    @staticmethod
    def create_new_session(initial_altitude: float = 1000.0, mode: str = "SIMULATION") -> Dict[str, Any]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            session = repo.create_session(initial_altitude=initial_altitude, mode=mode)
            return {
                "id": session.id,
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat() + "Z",
                "initial_altitude": session.initial_altitude,
                "mode": session.mode,
                "status": session.status
            }

    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            session = repo.get_session(session_id)
            if not session:
                return None
            return {
                "id": session.id,
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat() + "Z",
                "end_time": session.end_time.isoformat() + "Z" if session.end_time else None,
                "initial_altitude": session.initial_altitude,
                "final_altitude": session.final_altitude,
                "mode": session.mode,
                "status": session.status
            }

    @staticmethod
    def get_all_sessions() -> List[Dict[str, Any]]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            sessions = repo.get_all_sessions()
            return [
                {
                    "id": s.id,
                    "session_id": s.session_id,
                    "start_time": s.start_time.isoformat() + "Z",
                    "end_time": s.end_time.isoformat() + "Z" if s.end_time else None,
                    "initial_altitude": s.initial_altitude,
                    "final_altitude": s.final_altitude,
                    "mode": s.mode,
                    "status": s.status
                }
                for s in sessions
            ]

    @staticmethod
    def update_status(session_id: str, status: str, final_altitude: Optional[float] = None) -> Optional[Dict[str, Any]]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            session = repo.update_session_status(session_id, status, final_altitude)
            if not session:
                return None
            return {
                "id": session.id,
                "session_id": session.session_id,
                "start_time": session.start_time.isoformat() + "Z",
                "end_time": session.end_time.isoformat() + "Z" if session.end_time else None,
                "initial_altitude": session.initial_altitude,
                "final_altitude": session.final_altitude,
                "mode": session.mode,
                "status": session.status
            }

    @staticmethod
    def get_analytics(session_id: str) -> Dict[str, Any]:
        with SessionLocal() as db:
            repo = SystemRepository(db)
            return repo.get_session_analytics(session_id)

    @staticmethod
    def export_csv(session_id: str) -> str:
        """Generates comprehensive CSV containing telemetry, metrics, tracking, and events."""
        with SessionLocal() as db:
            telemetry = db.query(TelemetryModel).filter(TelemetryModel.session_id == session_id).order_by(TelemetryModel.timestamp).all()
            metrics = db.query(ComputerMetricsModel).filter(ComputerMetricsModel.session_id == session_id).order_by(ComputerMetricsModel.timestamp).all()
            tracking = db.query(TrackingModel).filter(TrackingModel.session_id == session_id).order_by(TrackingModel.timestamp).all()
            events = db.query(SystemEventModel).filter(SystemEventModel.session_id == session_id).order_by(SystemEventModel.timestamp).all()

        output = io.StringIO()
        writer = csv.writer(output)

        # 1. Telemetry & Compute Section
        writer.writerow(["=== TELEMETRY & COMPUTER METRICS ==="])
        writer.writerow([
            "Timestamp", "Altitude (m)", "Pressure (kPa)", "Temperature (C)", "Humidity (%)",
            "Vibration", "Air Density Ratio", "Cooling Effectiveness (%)",
            "CPU Usage (%)", "RAM Usage (%)", "CPU Temp (C)", "AI Latency (ms)", "FPS"
        ])
        
        # Merge telemetry and metrics by index/time
        count = min(len(telemetry), len(metrics))
        for i in range(count):
            t = telemetry[i]
            m = metrics[i]
            writer.writerow([
                t.timestamp.isoformat(),
                t.altitude, t.pressure, t.temperature, t.humidity,
                t.vibration, t.air_density, t.cooling_effectiveness,
                m.cpu_usage, m.ram_usage, m.cpu_temperature, m.ai_latency, m.fps
            ])

        writer.writerow([])
        # 2. Tracking Section
        writer.writerow(["=== SOFTWARE TRACKING LOG ==="])
        writer.writerow([
            "Timestamp", "Target X", "Target Y", "Error X", "Error Y",
            "Pan Angle (deg)", "Tilt Angle (deg)", "Tracking Confidence", "Status"
        ])
        for tr in tracking:
            writer.writerow([
                tr.timestamp.isoformat(),
                tr.target_x, tr.target_y, tr.error_x, tr.error_y,
                tr.pan_angle, tr.tilt_angle, tr.tracking_confidence, tr.status
            ])

        writer.writerow([])
        # 3. Events Section
        writer.writerow(["=== SYSTEM EVENTS ==="])
        writer.writerow(["Timestamp", "Severity", "Event Type", "Message"])
        for ev in events:
            writer.writerow([
                ev.timestamp.isoformat(),
                ev.severity, ev.event_type, ev.message
            ])

        return output.getvalue()
