"""
Computer Performance Simulation Model
Project: SIH PS 26050 - High Altitude Anti-Drone System (DRDO)

NOTE / DISCLAIMER:
"This is a prototype simulation relationship and not a validated thermal model."
This module models the coupled relationship between environmental cooling constraints at high altitudes,
compute workload, thermal equilibrium, and AI inference latency/FPS.
"""

import random
from typing import Dict, Any


class ComputerSimulator:
    def __init__(self):
        # Base steady-state parameters
        self.base_cpu_load = 35.0  # %
        self.user_cpu_load_factor = 0.0  # (0.0 to 1.0)
        self.ai_load_factor = 0.50  # (0.0 to 1.0)
        
        self.current_cpu_usage = 42.0
        self.current_ram_usage = 48.0
        self.current_cpu_temp = 52.0
        self.current_latency = 45.0
        self.current_fps = 22.0

    def set_workload(self, cpu_load_slider: float = 0.0, ai_load_slider: float = 0.5):
        """Configure user workload multipliers from frontend sliders."""
        self.user_cpu_load_factor = max(0.0, min(1.0, float(cpu_load_slider)))
        self.ai_load_factor = max(0.0, min(1.0, float(ai_load_slider)))

    def step(self, cooling_effectiveness: float, ambient_temp: float, dt: float = 1.0) -> Dict[str, Any]:
        """
        Calculates computer performance based on thermal dissipation and workload.
        
        Relationship chain:
        1. CPU Usage = base_load + ai_load_factor * 35% + user_load_slider * 30% + noise
        2. Thermal Dissipation Deficit:
           Lower cooling_effectiveness (e.g. 60-70% at 5000m) impedes heat removal.
        3. Target CPU Temperature = ambient_temp + (CPU_Usage * 0.55) * (100.0 / cooling_effectiveness)
        4. Throttling: If CPU Temp > 78°C, thermal throttling kicks in:
           - Increases inference latency
           - Decreases FPS
        """
        # 1. CPU Usage (%)
        target_cpu = self.base_cpu_load + (self.ai_load_factor * 30.0) + (self.user_cpu_load_factor * 35.0)
        cpu_noise = (random.random() - 0.5) * 4.0
        self.current_cpu_usage += (target_cpu + cpu_noise - self.current_cpu_usage) * min(1.0, dt * 0.8)
        self.current_cpu_usage = max(10.0, min(100.0, self.current_cpu_usage))

        # 2. RAM Usage (%)
        target_ram = 45.0 + (self.ai_load_factor * 20.0) + (self.user_cpu_load_factor * 10.0)
        ram_noise = (random.random() - 0.5) * 1.5
        self.current_ram_usage += (target_ram + ram_noise - self.current_ram_usage) * min(1.0, dt * 0.3)
        self.current_ram_usage = max(20.0, min(95.0, self.current_ram_usage))

        # 3. CPU Temperature (°C)
        # Cooling factor ratio: 100% cooling -> multiplier 1.0; 60% cooling -> multiplier 1.45
        cooling_ratio = 100.0 / max(35.0, cooling_effectiveness)
        heat_generated = (self.current_cpu_usage * 0.48) * cooling_ratio
        
        # Equilibrium CPU temperature
        target_temp = max(35.0, ambient_temp + heat_generated)
        temp_rate = 0.25 * dt  # thermal mass inertia
        self.current_cpu_temp += (target_temp - self.current_cpu_temp) * min(1.0, temp_rate)
        self.current_cpu_temp = max(20.0, min(105.0, self.current_cpu_temp + (random.random() - 0.5) * 0.4))

        # 4. Thermal Throttling & AI Latency (ms)
        # Baseline latency ~38ms for lightweight YOLOv8n
        base_latency = 35.0 + (self.ai_load_factor * 25.0)
        throttling_penalty = 0.0
        if self.current_cpu_temp > 75.0:
            # Progressive throttling delay
            throttling_penalty = (self.current_cpu_temp - 75.0) ** 1.35 * 3.5

        target_latency = base_latency + throttling_penalty + (self.current_cpu_usage * 0.15)
        lat_noise = (random.random() - 0.5) * 3.0
        self.current_latency += (target_latency + lat_noise - self.current_latency) * min(1.0, dt * 0.9)
        self.current_latency = max(15.0, min(300.0, self.current_latency))

        # 5. Effective Processing FPS
        # FPS inversely related to latency with processing overhead
        target_fps = 1000.0 / (self.current_latency + 10.0)
        # High CPU saturation can drop frames
        if self.current_cpu_usage > 90.0:
            target_fps *= 0.85
        
        fps_noise = (random.random() - 0.5) * 0.8
        self.current_fps += (target_fps + fps_noise - self.current_fps) * min(1.0, dt * 0.9)
        self.current_fps = max(1.0, min(60.0, self.current_fps))

        return {
            "cpu_usage": round(self.current_cpu_usage, 1),
            "ram_usage": round(self.current_ram_usage, 1),
            "cpu_temperature": round(self.current_cpu_temp, 1),
            "ai_latency": round(self.current_latency, 1),
            "fps": round(self.current_fps, 1)
        }
