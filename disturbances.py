"""
Preset disturbance scenarios and parameter structures for simulation.
Project: SIH PS 26050 - High Altitude Anti-Drone System (DRDO)
"""

from typing import Dict, Any


SCENARIOS: Dict[str, Dict[str, Any]] = {
    "NORMAL": {
        "name": "Normal Baseline",
        "description": "Standard low-altitude baseline operation (1000m, minimal vibration, nominal load)",
        "altitude": 1000.0,
        "vibration": 0.05,
        "env_variation": 0.15,
        "cpu_load": 0.10,
        "ai_load": 0.40,
        "base_temp": 25.0
    },
    "HIGH_ALTITUDE": {
        "name": "High Altitude Deployment",
        "description": "Extreme altitude elevation (5000m) with reduced air density and impaired thermal cooling",
        "altitude": 5000.0,
        "vibration": 0.20,
        "env_variation": 0.35,
        "cpu_load": 0.25,
        "ai_load": 0.50,
        "base_temp": 20.0
    },
    "COLD_ENVIRONMENT": {
        "name": "Sub-Zero Cold Environment",
        "description": "Sub-zero ambient conditions with cold-induced atmospheric variance",
        "altitude": 3500.0,
        "vibration": 0.15,
        "env_variation": 0.40,
        "cpu_load": 0.20,
        "ai_load": 0.40,
        "base_temp": -5.0
    },
    "HIGH_VIBRATION": {
        "name": "Mechanical Vibration Disturbance",
        "description": "Severe platform resonance / wind buffeting degrading tracking optical stability",
        "altitude": 2000.0,
        "vibration": 0.85,
        "env_variation": 0.30,
        "cpu_load": 0.30,
        "ai_load": 0.50,
        "base_temp": 22.0
    },
    "HIGH_COMPUTER_LOAD": {
        "name": "Compute Saturation Stress",
        "description": "Intense multi-stream AI processing workload generating peak heat flux",
        "altitude": 1500.0,
        "vibration": 0.10,
        "env_variation": 0.20,
        "cpu_load": 0.90,
        "ai_load": 0.95,
        "base_temp": 25.0
    },
    "COMBINED_STRESS": {
        "name": "Combined Mission Stress Test",
        "description": "Simultaneous peak altitude (5500m), severe vibration (80%), and compute saturation",
        "altitude": 5500.0,
        "vibration": 0.80,
        "env_variation": 0.50,
        "cpu_load": 0.85,
        "ai_load": 0.90,
        "base_temp": 15.0
    }
}
