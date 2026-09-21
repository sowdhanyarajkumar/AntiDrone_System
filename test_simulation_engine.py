import pytest
from app.simulation.engine import SimulationEngine
from app.simulation.disturbances import SCENARIOS


def test_simulation_engine_state_generation():
    engine = SimulationEngine(tick_seconds=0.5, default_altitude=1500.0)
    state = engine.generate_current_state()

    assert "environment" in state
    assert "computer" in state
    assert "tracking" in state
    assert "timestamp" in state

    assert 0 <= state["environment"]["altitude"] <= 6000
    assert 0 <= state["computer"]["cpu_usage"] <= 100
    assert state["computer"]["fps"] > 0
    assert 0 <= state["tracking"]["pan_angle"] <= 180
    assert 0 <= state["tracking"]["tilt_angle"] <= 180


def test_scenario_presets_application():
    engine = SimulationEngine()
    assert engine.apply_scenario("HIGH_ALTITUDE")
    assert engine.env_sim.target_altitude == 5000.0
    assert engine.current_scenario_name == "HIGH_ALTITUDE"

    assert engine.apply_scenario("COMBINED_STRESS")
    assert engine.env_sim.target_altitude == 5500.0
    assert engine.env_sim.vibration_disturbance == 0.80

    assert not engine.apply_scenario("NON_EXISTENT_SCENARIO")
