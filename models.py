import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Index
from app.database.database import Base


class SessionModel(Base):
    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), unique=True, index=True, nullable=False)
    start_time = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    end_time = Column(DateTime, nullable=True)
    initial_altitude = Column(Float, default=1000.0)
    final_altitude = Column(Float, nullable=True)
    mode = Column(String(32), default="SIMULATION")
    status = Column(String(32), default="ACTIVE")  # ACTIVE, PAUSED, COMPLETED, STOPPED


class TelemetryModel(Base):
    __tablename__ = "telemetry"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    altitude = Column(Float, nullable=False)
    temperature = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    vibration = Column(Float, nullable=False)
    air_density = Column(Float, nullable=False)
    cooling_effectiveness = Column(Float, nullable=False)


class ComputerMetricsModel(Base):
    __tablename__ = "computer_metrics"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    cpu_usage = Column(Float, nullable=False)
    ram_usage = Column(Float, nullable=False)
    cpu_temperature = Column(Float, nullable=False)
    ai_latency = Column(Float, nullable=False)
    fps = Column(Float, nullable=False)


class DetectionModel(Base):
    __tablename__ = "detections"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    class_name = Column(String(64), default="drone")
    confidence = Column(Float, nullable=False)
    x = Column(Float, nullable=False)
    y = Column(Float, nullable=False)
    width = Column(Float, nullable=False)
    height = Column(Float, nullable=False)
    center_x = Column(Float, nullable=False)
    center_y = Column(Float, nullable=False)
    tracking_id = Column(String(32), nullable=True)
    fps = Column(Float, nullable=False)
    inference_latency = Column(Float, nullable=False)


class TrackingModel(Base):
    __tablename__ = "tracking"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    target_x = Column(Float, nullable=False)
    target_y = Column(Float, nullable=False)
    image_center_x = Column(Float, default=320.0)
    image_center_y = Column(Float, default=240.0)
    error_x = Column(Float, nullable=False)
    error_y = Column(Float, nullable=False)
    pan_angle = Column(Float, nullable=False)
    tilt_angle = Column(Float, nullable=False)
    tracking_confidence = Column(Float, nullable=False)
    status = Column(String(32), default="LOCKED")  # SEARCHING, ACQUIRING, LOCKED, LOST


class SystemEventModel(Base):
    __tablename__ = "system_events"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(64), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, nullable=False, index=True)
    severity = Column(String(32), default="INFO")  # INFO, WARNING, DEGRADED, CRITICAL
    event_type = Column(String(32), default="SYSTEM")  # SYSTEM, SIMULATION, ENVIRONMENT, AI, TRACKING, PERFORMANCE
    message = Column(Text, nullable=False)
