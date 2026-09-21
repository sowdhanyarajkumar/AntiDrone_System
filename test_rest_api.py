import pytest


def test_health_and_status_endpoints(client):
    res_health = client.get("/api/health")
    assert res_health.status_code == 200
    assert res_health.json()["status"] == "healthy"

    res_status = client.get("/api/system/status")
    assert res_status.status_code == 200
    assert "system" in res_status.json()


def test_simulation_controls_and_sessions(client):
    # Start simulation
    res_start = client.post("/api/simulation/start", json={"initial_altitude": 2000.0})
    assert res_start.status_code == 200
    session_id = res_start.json()["session"]["session_id"]
    assert session_id.startswith("HA-2026-")

    # Update config
    res_cfg = client.post("/api/simulation/config", json={"altitude": 3500.0, "vibration": 0.4})
    assert res_cfg.status_code == 200

    # Stop simulation
    res_stop = client.post("/api/simulation/stop")
    assert res_stop.status_code == 200

    # Session detail
    res_detail = client.get(f"/api/sessions/{session_id}")
    assert res_detail.status_code == 200
    assert res_detail.json()["session"]["session_id"] == session_id

    # Export CSV
    res_csv = client.get(f"/api/sessions/{session_id}/export")
    assert res_csv.status_code == 200
    assert "TELEMETRY" in res_csv.text


def test_analysis_performance_endpoint(client):
    res = client.get("/api/analysis/performance")
    assert res.status_code == 200
    data = res.json()
    assert "curve_data" in data
    assert "comparison" in data
    assert len(data["curve_data"]) >= 10
