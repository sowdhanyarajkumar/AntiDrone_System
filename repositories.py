import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from app.database.models import (
    SessionModel,
    TelemetryModel,
    ComputerMetricsModel,
    DetectionModel,
    TrackingModel,
    SystemEventModel,
)


class SystemRepository:
    def __init__(self, db: Session):
        self.db = db

    # ------------------ SESSIONS ------------------
    def create_session(self, initial_altitude: float = 1000.0, mode: str = "SIMULATION") -> SessionModel:
        # Generate clean sequential ID: HA-2026-0001
        count = self.db.query(SessionModel).count() + 1
        session_id = f"HA-2026-{count:04d}"
        
        session = SessionModel(
            session_id=session_id,
            start_time=datetime.datetime.utcnow(),
            initial_altitude=initial_altitude,
            mode=mode,
            status="ACTIVE"
        )
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def get_session(self, session_id: str) -> Optional[SessionModel]:
        return self.db.query(SessionModel).filter(SessionModel.session_id == session_id).first()

    def get_active_session(self) -> Optional[SessionModel]:
        return self.db.query(SessionModel).filter(SessionModel.status.in_(["ACTIVE", "PAUSED"])).order_by(desc(SessionModel.start_time)).first()

    def get_all_sessions(self) -> List[SessionModel]:
        return self.db.query(SessionModel).order_by(desc(SessionModel.start_time)).all()

    def update_session_status(self, session_id: str, status: str, final_altitude: Optional[float] = None) -> Optional[SessionModel]:
        session = self.get_session(session_id)
        if session:
            session.status = status
            if status in ["COMPLETED", "STOPPED"]:
                session.end_time = datetime.datetime.utcnow()
                if final_altitude is not None:
                    session.final_altitude = final_altitude
            self.db.commit()
            self.db.refresh(session)
        return session

    # ------------------ TELEMETRY ------------------
    def add_telemetry(self, session_id: str, data: Dict[str, Any]) -> TelemetryModel:
        record = TelemetryModel(
            session_id=session_id,
            timestamp=datetime.datetime.utcnow(),
            altitude=data["altitude"],
            temperature=data["temperature"],
            pressure=data["pressure"],
            humidity=data["humidity"],
            vibration=data["vibration"],
            air_density=data["air_density"],
            cooling_effectiveness=data["cooling_effectiveness"]
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_latest_telemetry(self, session_id: Optional[str] = None) -> Optional[TelemetryModel]:
        q = self.db.query(TelemetryModel)
        if session_id:
            q = q.filter(TelemetryModel.session_id == session_id)
        return q.order_by(desc(TelemetryModel.timestamp)).first()

    def get_telemetry_history(self, session_id: Optional[str] = None, limit: int = 100) -> List[TelemetryModel]:
        q = self.db.query(TelemetryModel)
        if session_id:
            q = q.filter(TelemetryModel.session_id == session_id)
        return q.order_by(desc(TelemetryModel.timestamp)).limit(limit).all()

    # ------------------ COMPUTER METRICS ------------------
    def add_computer_metrics(self, session_id: str, data: Dict[str, Any]) -> ComputerMetricsModel:
        record = ComputerMetricsModel(
            session_id=session_id,
            timestamp=datetime.datetime.utcnow(),
            cpu_usage=data["cpu_usage"],
            ram_usage=data["ram_usage"],
            cpu_temperature=data["cpu_temperature"],
            ai_latency=data["ai_latency"],
            fps=data["fps"]
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_latest_computer_metrics(self, session_id: Optional[str] = None) -> Optional[ComputerMetricsModel]:
        q = self.db.query(ComputerMetricsModel)
        if session_id:
            q = q.filter(ComputerMetricsModel.session_id == session_id)
        return q.order_by(desc(ComputerMetricsModel.timestamp)).first()

    def get_computer_history(self, session_id: Optional[str] = None, limit: int = 100) -> List[ComputerMetricsModel]:
        q = self.db.query(ComputerMetricsModel)
        if session_id:
            q = q.filter(ComputerMetricsModel.session_id == session_id)
        return q.order_by(desc(ComputerMetricsModel.timestamp)).limit(limit).all()

    # ------------------ DETECTIONS ------------------
    def add_detection(self, session_id: str, data: Dict[str, Any]) -> DetectionModel:
        record = DetectionModel(
            session_id=session_id,
            timestamp=datetime.datetime.utcnow(),
            class_name=data.get("class_name", "drone"),
            confidence=data["confidence"],
            x=data["x"],
            y=data["y"],
            width=data["width"],
            height=data["height"],
            center_x=data["center_x"],
            center_y=data["center_y"],
            tracking_id=str(data.get("tracking_id", "")),
            fps=data.get("fps", 0.0),
            inference_latency=data.get("inference_latency", 0.0)
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_latest_detections(self, session_id: Optional[str] = None, limit: int = 20) -> List[DetectionModel]:
        q = self.db.query(DetectionModel)
        if session_id:
            q = q.filter(DetectionModel.session_id == session_id)
        return q.order_by(desc(DetectionModel.timestamp)).limit(limit).all()

    # ------------------ TRACKING ------------------
    def add_tracking(self, session_id: str, data: Dict[str, Any]) -> TrackingModel:
        record = TrackingModel(
            session_id=session_id,
            timestamp=datetime.datetime.utcnow(),
            target_x=data["target_x"],
            target_y=data["target_y"],
            image_center_x=data.get("image_center_x", 320.0),
            image_center_y=data.get("image_center_y", 240.0),
            error_x=data["error_x"],
            error_y=data["error_y"],
            pan_angle=data["pan_angle"],
            tilt_angle=data["tilt_angle"],
            tracking_confidence=data["confidence"],
            status=data.get("status", "LOCKED")
        )
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_latest_tracking(self, session_id: Optional[str] = None) -> Optional[TrackingModel]:
        q = self.db.query(TrackingModel)
        if session_id:
            q = q.filter(TrackingModel.session_id == session_id)
        return q.order_by(desc(TrackingModel.timestamp)).first()

    def get_tracking_history(self, session_id: Optional[str] = None, limit: int = 100) -> List[TrackingModel]:
        q = self.db.query(TrackingModel)
        if session_id:
            q = q.filter(TrackingModel.session_id == session_id)
        return q.order_by(desc(TrackingModel.timestamp)).limit(limit).all()

    # ------------------ EVENTS ------------------
    def add_event(self, session_id: str, severity: str, event_type: str, message: str) -> SystemEventModel:
        event = SystemEventModel(
            session_id=session_id,
            timestamp=datetime.datetime.utcnow(),
            severity=severity,
            event_type=event_type,
            message=message
        )
        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)
        return event

    def get_events(self, session_id: Optional[str] = None, limit: int = 100) -> List[SystemEventModel]:
        q = self.db.query(SystemEventModel)
        if session_id:
            q = q.filter(SystemEventModel.session_id == session_id)
        return q.order_by(desc(SystemEventModel.timestamp)).limit(limit).all()

    # ------------------ ANALYTICS & SUMMARIES ------------------
    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        session = self.get_session(session_id)
        if not session:
            return {}

        tel_count = self.db.query(func.count(TelemetryModel.id)).filter(TelemetryModel.session_id == session_id).scalar() or 0
        events_count = self.db.query(func.count(SystemEventModel.id)).filter(SystemEventModel.session_id == session_id).scalar() or 0
        det_count = self.db.query(func.count(DetectionModel.id)).filter(DetectionModel.session_id == session_id).scalar() or 0
        
        warn_count = self.db.query(func.count(SystemEventModel.id)).filter(
            SystemEventModel.session_id == session_id,
            SystemEventModel.severity == "WARNING"
        ).scalar() or 0
        
        crit_count = self.db.query(func.count(SystemEventModel.id)).filter(
            SystemEventModel.session_id == session_id,
            SystemEventModel.severity == "CRITICAL"
        ).scalar() or 0

        # Telemetry aggregations
        tel_stats = self.db.query(
            func.avg(TelemetryModel.temperature),
            func.max(TelemetryModel.temperature),
            func.max(TelemetryModel.vibration)
        ).filter(TelemetryModel.session_id == session_id).first()

        # Computer metrics aggregations
        comp_stats = self.db.query(
            func.avg(ComputerMetricsModel.cpu_usage),
            func.max(ComputerMetricsModel.cpu_temperature),
            func.avg(ComputerMetricsModel.fps),
            func.min(ComputerMetricsModel.fps),
            func.avg(ComputerMetricsModel.ai_latency),
            func.max(ComputerMetricsModel.ai_latency)
        ).filter(ComputerMetricsModel.session_id == session_id).first()

        # Tracking aggregations
        track_stats = self.db.query(
            func.avg(TrackingModel.tracking_confidence)
        ).filter(TrackingModel.session_id == session_id).first()

        duration = 0.0
        if session.end_time:
            duration = (session.end_time - session.start_time).total_seconds()
        elif tel_count > 0:
            latest = self.get_latest_telemetry(session_id)
            if latest:
                duration = (latest.timestamp - session.start_time).total_seconds()

        return {
            "session_id": session.session_id,
            "start_time": session.start_time.isoformat(),
            "end_time": session.end_time.isoformat() if session.end_time else None,
            "duration_seconds": round(max(0.0, duration), 1),
            "initial_altitude": session.initial_altitude,
            "final_altitude": session.final_altitude,
            "mode": session.mode,
            "status": session.status,
            "telemetry_count": tel_count,
            "events_count": events_count,
            "detections_count": det_count,
            "avg_temperature": round(tel_stats[0], 2) if tel_stats and tel_stats[0] is not None else None,
            "max_temperature": round(tel_stats[1], 2) if tel_stats and tel_stats[1] is not None else None,
            "max_vibration": round(tel_stats[2], 3) if tel_stats and tel_stats[2] is not None else None,
            "avg_cpu_usage": round(comp_stats[0], 1) if comp_stats and comp_stats[0] is not None else None,
            "max_cpu_temp": round(comp_stats[1], 1) if comp_stats and comp_stats[1] is not None else None,
            "avg_fps": round(comp_stats[2], 1) if comp_stats and comp_stats[2] is not None else None,
            "min_fps": round(comp_stats[3], 1) if comp_stats and comp_stats[3] is not None else None,
            "avg_latency": round(comp_stats[4], 1) if comp_stats and comp_stats[4] is not None else None,
            "max_latency": round(comp_stats[5], 1) if comp_stats and comp_stats[5] is not None else None,
            "avg_tracking_confidence": round(track_stats[0], 2) if track_stats and track_stats[0] is not None else None,
            "warning_count": warn_count,
            "critical_count": crit_count
        }
