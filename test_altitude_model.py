import pytest
from app.simulation.environment import EnvironmentSimulator


def test_altitude_pressure_temperature_relationship():
    sim_low = EnvironmentSimulator(altitude=0.0)
    low_res = sim_low.step(dt=1.0)

    sim_mid = EnvironmentSimulator(altitude=2500.0)
    mid_res = sim_mid.step(dt=1.0)

    sim_high = EnvironmentSimulator(altitude=5000.0)
    high_res = sim_high.step(dt=1.0)

    # Pressure must decrease monotonically with altitude
    assert low_res["pressure"] > mid_res["pressure"] > high_res["pressure"]
    assert low_res["pressure_hpa"] > mid_res["pressure_hpa"] > high_res["pressure_hpa"]

    # Temperature must decrease with altitude
    assert low_res["temperature"] > mid_res["temperature"] > high_res["temperature"]

    # Air density indicator must decrease with altitude
    assert low_res["air_density"] > mid_res["air_density"] > high_res["air_density"]

    # Cooling effectiveness must decrease with altitude
    assert low_res["cooling_effectiveness"] > mid_res["cooling_effectiveness"] > high_res["cooling_effectiveness"]


def test_altitude_limits_and_vibration():
    sim = EnvironmentSimulator(altitude=1000.0)
    sim.set_altitude(7000.0)  # Clamped to 6000m
    assert sim.target_altitude == 6000.0

    sim.set_altitude(-500.0)  # Clamped to 0m
    assert sim.target_altitude == 0.0

    # Disturbance tests
    sim.set_disturbances(vibration=0.85)
    res = sim.step(dt=1.0)
    assert res["vibration"] > 0.50
