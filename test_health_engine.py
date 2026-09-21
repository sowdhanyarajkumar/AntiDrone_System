import pytest
from app.services.health_service import HealthEngine


def test_health_engine_normal():
    engine = HealthEngine()
    env = {"vibration": 0.05, "cooling_effectiveness": 95.0}
    comp = {"cpu_temperature": 52.0, "cpu_usage": 40.0, "fps": 24.0, "ai_latency": 38.0}
    track = {"confidence": 0.92}

    res = engine.evaluate(env, comp, track)
    assert res["status"] == "NORMAL"
    assert res["score"] >= 85


def test_health_engine_warning_and_critical():
    engine = HealthEngine()
    
    # Warning on elevated CPU temp
    env = {"vibration": 0.05, "cooling_effectiveness": 70.0}
    comp = {"cpu_temperature": 77.0, "cpu_usage": 50.0, "fps": 20.0, "ai_latency": 45.0}
    track = {"confidence": 0.88}
    res_warn = engine.evaluate(env, comp, track)
    assert res_warn["status"] in ["WARNING", "DEGRADED"]
    assert any("temperature" in r.lower() for r in res_warn["reasons"])

    # Critical on extreme thermal stress
    comp_crit = {"cpu_temperature": 89.0, "cpu_usage": 98.0, "fps": 4.0, "ai_latency": 160.0}
    res_crit = engine.evaluate(env, comp_crit, track)
    assert res_crit["status"] == "CRITICAL"
    assert res_crit["score"] < 50
