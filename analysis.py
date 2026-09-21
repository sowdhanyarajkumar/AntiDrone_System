from fastapi import APIRouter
from typing import Dict, Any, List
from app.simulation.environment import EnvironmentSimulator
from app.simulation.computer import ComputerSimulator
from app.ai.tracker import SoftwareTracker

router = APIRouter()


@router.get("/analysis/performance")
def get_performance_analysis():
    """
    Computes altitude-performance correlation curves across 0m to 6000m.
    Shows the direct relationship between altitude, cooling degradation, compute throttling, and tracking confidence.
    """
    altitudes = [0, 500, 1000, 1500, 2000, 2500, 3000, 3500, 4000, 4500, 5000, 5500, 6000]
    curve_data: List[Dict[str, Any]] = []

    for alt in altitudes:
        env_sim = EnvironmentSimulator(altitude=alt)
        comp_sim = ComputerSimulator()
        tracker = SoftwareTracker()

        env_state = env_sim.step(dt=1.0)
        # Step computer to reach near-steady state
        for _ in range(5):
            comp_state = comp_sim.step(
                cooling_effectiveness=env_state["cooling_effectiveness"],
                ambient_temp=env_state["temperature"],
                dt=1.0
            )

        track_state = tracker.solve(target_x=360.0, target_y=270.0, confidence=0.90, vibration=env_state["vibration"])

        curve_data.append({
            "altitude": alt,
            "pressure": env_state["pressure"],
            "temperature": env_state["temperature"],
            "cooling_effectiveness": env_state["cooling_effectiveness"],
            "air_density": env_state["air_density"],
            "cpu_temperature": comp_state["cpu_temperature"],
            "ai_latency": comp_state["ai_latency"],
            "fps": comp_state["fps"],
            "tracking_confidence": track_state["confidence"]
        })

    # Comparative analysis: Normal Baseline (1000m) vs High-Altitude Extreme (5000m)
    baseline = next(d for d in curve_data if d["altitude"] == 1000)
    extreme = next(d for d in curve_data if d["altitude"] == 5000)

    comparison = {
        "metrics": [
            {
                "parameter": "Atmospheric Pressure",
                "unit": "kPa",
                "baseline_1000m": baseline["pressure"],
                "high_altitude_5000m": extreme["pressure"],
                "delta": round(extreme["pressure"] - baseline["pressure"], 2),
                "pct_change": f"{round(((extreme['pressure'] - baseline['pressure']) / baseline['pressure']) * 100, 1)}%"
            },
            {
                "parameter": "Ambient Temperature",
                "unit": "°C",
                "baseline_1000m": baseline["temperature"],
                "high_altitude_5000m": extreme["temperature"],
                "delta": round(extreme["temperature"] - baseline["temperature"], 2),
                "pct_change": f"{round(extreme['temperature'] - baseline['temperature'], 1)}°C"
            },
            {
                "parameter": "Cooling Effectiveness",
                "unit": "%",
                "baseline_1000m": baseline["cooling_effectiveness"],
                "high_altitude_5000m": extreme["cooling_effectiveness"],
                "delta": round(extreme["cooling_effectiveness"] - baseline["cooling_effectiveness"], 1),
                "pct_change": f"{round(((extreme['cooling_effectiveness'] - baseline['cooling_effectiveness']) / baseline['cooling_effectiveness']) * 100, 1)}%"
            },
            {
                "parameter": "CPU Core Temperature",
                "unit": "°C",
                "baseline_1000m": baseline["cpu_temperature"],
                "high_altitude_5000m": extreme["cpu_temperature"],
                "delta": round(extreme["cpu_temperature"] - baseline["cpu_temperature"], 1),
                "pct_change": f"{round(((extreme['cpu_temperature'] - baseline['cpu_temperature']) / baseline['cpu_temperature']) * 100, 1)}%"
            },
            {
                "parameter": "AI Inference Latency",
                "unit": "ms",
                "baseline_1000m": baseline["ai_latency"],
                "high_altitude_5000m": extreme["ai_latency"],
                "delta": round(extreme["ai_latency"] - baseline["ai_latency"], 1),
                "pct_change": f"+{round(((extreme['ai_latency'] - baseline['ai_latency']) / baseline['ai_latency']) * 100, 1)}%"
            },
            {
                "parameter": "Processing Frame Rate",
                "unit": "FPS",
                "baseline_1000m": baseline["fps"],
                "high_altitude_5000m": extreme["fps"],
                "delta": round(extreme["fps"] - baseline["fps"], 1),
                "pct_change": f"{round(((extreme['fps'] - baseline['fps']) / baseline['fps']) * 100, 1)}%"
            },
            {
                "parameter": "Tracking Optical Confidence",
                "unit": "ratio",
                "baseline_1000m": baseline["tracking_confidence"],
                "high_altitude_5000m": extreme["tracking_confidence"],
                "delta": round(extreme["tracking_confidence"] - baseline["tracking_confidence"], 2),
                "pct_change": f"{round(((extreme['tracking_confidence'] - baseline['tracking_confidence']) / baseline['tracking_confidence']) * 100, 1)}%"
            }
        ],
        "notes": "Prototype Simulation Model — Demonstrates thermal dissipation constraints in rarefied atmosphere."
    }

    return {
        "curve_data": curve_data,
        "comparison": comparison
    }
