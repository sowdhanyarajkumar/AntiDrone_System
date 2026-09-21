import pytest
from app.database.database import SessionLocal
from app.database.repositories import SystemRepository


def test_session_lifecycle_and_telemetry():
    with SessionLocal() as db:
        repo = SystemRepository(db)
        # Create session
        session = repo.create_session(initial_altitude=1200.0, mode="TEST_MODE")
        sid = session.session_id
        assert sid.startswith("HA-2026-")

        # Insert telemetry
        tel_data = {
            "altitude": 1200.0,
            "temperature": 17.2,
            "pressure": 87.5,
            "humidity": 45.0,
            "vibration": 0.08,
            "air_density": 0.95,
            "cooling_effectiveness": 92.0
        }
        repo.add_telemetry(sid, tel_data)
        
        # Insert computer metrics
        comp_data = {
            "cpu_usage": 45.0,
            "ram_usage": 50.0,
            "cpu_temperature": 55.0,
            "ai_latency": 35.0,
            "fps": 24.0
        }
        repo.add_computer_metrics(sid, comp_data)

        # Retrieve
        latest_tel = repo.get_latest_telemetry(sid)
        assert latest_tel is not None
        assert latest_tel.altitude == 1200.0

        # Analytics
        analytics = repo.get_session_analytics(sid)
        assert analytics["telemetry_count"] >= 1
        assert analytics["session_id"] == sid

        # Complete session
        repo.update_session_status(sid, "COMPLETED", final_altitude=1500.0)
        updated = repo.get_session(sid)
        assert updated.status == "COMPLETED"
