"""
Main Simulation Engine orchestrating environmental, thermal, and tracking dynamics.
Project: SIH PS 26050 - High Altitude Anti-Drone System (DRDO)
"""

import asyncio
import math
import random
import datetime
from typing import Dict, Any, Optional, Callable, List
from app.simulation.environment import EnvironmentSimulator
from app.simulation.computer import ComputerSimulator
from app.simulation.disturbances import SCENARIOS


class SimulationEngine:
    def __init__(self, tick_seconds: float = 1.0, default_altitude: float = 1000.0):
        self.tick_seconds = float(tick_seconds)
        self.env_sim = EnvironmentSimulator(altitude=default_altitude)
        self.comp_sim = ComputerSimulator()
        
        # Operational State
        self.is_running = False
        self.is_paused = False
        self.current_session_id: Optional[str] = None
        self.current_scenario_name = "NORMAL"
        
        # Synthetic Target Tracker Dynamics (for when simulated AI mode is active)
        # Bounded trajectory of a simulated drone across a 640x480 pixel frame
        self.target_x = 320.0
        self.target_y = 200.0
        self.target_vx = 3.5
        self.target_vy = 1.8
        self.tracking_confidence = 0.92
        self.tracking_status = "LOCKED"
        
        # Callbacks for telemetry ticks and events
        self._on_tick_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        self._on_event_callbacks: List[Callable[[str, str, str], None]] = []
        
        # Background task handle
        self._task: Optional[asyncio.Task] = None

    def register_tick_callback(self, cb: Callable[[Dict[str, Any]], None]):
        self._on_tick_callbacks.append(cb)

    def register_event_callback(self, cb: Callable[[str, str, str], None]):
        self._on_event_callbacks.append(cb)

    def apply_scenario(self, scenario_key: str):
        if scenario_key not in SCENARIOS:
            return False
        config = SCENARIOS[scenario_key]
        self.current_scenario_name = scenario_key
        self.env_sim.set_altitude(config["altitude"])
        self.env_sim.base_sea_level_temp = config["base_temp"]
        self.env_sim.set_disturbances(
            vibration=config["vibration"],
            env_variation=config["env_variation"]
        )
        self.comp_sim.set_workload(
            cpu_load_slider=config["cpu_load"],
            ai_load_slider=config["ai_load"]
        )
        self.emit_event("INFO", "SIMULATION", f"Applied scenario preset: {config['name']}")
        return True

    def set_altitude(self, altitude_m: float):
        self.env_sim.set_altitude(altitude_m)
        self.emit_event("INFO", "ENVIRONMENT", f"Target altitude adjusted to {round(altitude_m)} m")

    def set_vibration(self, vibration_ratio: float):
        self.env_sim.set_disturbances(
            vibration=vibration_ratio,
            env_variation=self.env_sim.env_variation_disturbance
        )
        if vibration_ratio > 0.6:
            self.emit_event("WARNING", "ENVIRONMENT", f"Elevated mechanical vibration detected ({round(vibration_ratio * 100)}%)")

    def set_compute_load(self, load_ratio: float):
        self.comp_sim.set_workload(
            cpu_load_slider=load_ratio,
            ai_load_slider=self.comp_sim.ai_load_factor
        )

    def set_ai_load(self, ai_load_ratio: float):
        self.comp_sim.set_workload(
            cpu_load_slider=self.comp_sim.user_cpu_load_factor,
            ai_load_slider=ai_load_ratio
        )

    def emit_event(self, severity: str, event_type: str, message: str):
        for cb in self._on_event_callbacks:
            try:
                cb(severity, event_type, message)
            except Exception:
                pass

    def start(self, session_id: str):
        self.current_session_id = session_id
        self.is_running = True
        self.is_paused = False
        self.emit_event("INFO", "SIMULATION", f"Simulation session {session_id} initiated")
        try:
            loop = asyncio.get_running_loop()
            if self._task is None or self._task.done():
                self._task = loop.create_task(self._run_loop())
        except RuntimeError:
            pass

    def pause(self):
        if self.is_running:
            self.is_paused = True
            self.emit_event("INFO", "SIMULATION", f"Simulation session {self.current_session_id} paused")

    def resume(self):
        if self.is_running and self.is_paused:
            self.is_paused = False
            self.emit_event("INFO", "SIMULATION", f"Simulation session {self.current_session_id} resumed")

    def stop(self):
        if self.is_running:
            self.is_running = False
            self.is_paused = False
            self.emit_event("INFO", "SIMULATION", f"Simulation session {self.current_session_id} concluded")
            if self._task and not self._task.done():
                self._task.cancel()
                self._task = None

    def reset(self):
        self.stop()
        self.env_sim = EnvironmentSimulator()
        self.comp_sim = ComputerSimulator()
        self.current_session_id = None
        self.target_x = 320.0
        self.target_y = 200.0

    def _step_target_tracking(self, vibration: float) -> Dict[str, Any]:
        """
        Calculates simulated target position and camera pan/tilt tracking solver.
        Frame dimensions: 640x480 (Image Center: 320, 240)
        """
        # Move target with boundary bounce
        self.target_x += self.target_vx
        self.target_y += self.target_vy

        if self.target_x <= 80 or self.target_x >= 560:
            self.target_vx = -self.target_vx
        if self.target_y <= 60 or self.target_y >= 400:
            self.target_vy = -self.target_vy

        # Target center and image center
        img_center_x = 320.0
        img_center_y = 240.0
        
        # Pixel errors relative to optical boresight
        error_x = round(self.target_x - img_center_x, 1)
        error_y = round(self.target_y - img_center_y, 1)

        # Software pan/tilt servo solver:
        # Standard pan range: 0° to 180° (neutral at 90°)
        # Standard tilt range: 0° to 180° (neutral at 90°)
        # Angle delta = (error / half_span) * max_deflection_deg (e.g. 45°)
        pan_angle = round(90.0 + (error_x / 320.0) * 45.0, 1)
        tilt_angle = round(90.0 - (error_y / 240.0) * 35.0, 1)

        # Tracking Confidence: degraded by high vibration and large offset
        offset_dist = math.sqrt(error_x**2 + error_y**2)
        base_confidence = max(0.40, 0.96 - (offset_dist / 600.0) * 0.20)
        
        # Vibration degradation penalty
        if vibration > 0.40:
            vib_penalty = (vibration - 0.40) * 0.45
            base_confidence -= vib_penalty

        self.tracking_confidence = round(max(0.15, min(0.99, base_confidence + (random.random() - 0.5) * 0.04)), 2)

        if self.tracking_confidence > 0.70:
            self.tracking_status = "LOCKED"
        elif self.tracking_confidence > 0.40:
            self.tracking_status = "ACQUIRING"
        else:
            self.tracking_status = "DEGRADED"

        return {
            "active": True,
            "target_x": round(self.target_x, 1),
            "target_y": round(self.target_y, 1),
            "image_center_x": img_center_x,
            "image_center_y": img_center_y,
            "error_x": error_x,
            "error_y": error_y,
            "pan_angle": pan_angle,
            "tilt_angle": tilt_angle,
            "confidence": self.tracking_confidence,
            "status": self.tracking_status
        }

    def generate_current_state(self) -> Dict[str, Any]:
        """Produce an instantaneous snapshot of the simulation state."""
        env_data = self.env_sim.step(dt=self.tick_seconds)
        comp_data = self.comp_sim.step(
            cooling_effectiveness=env_data["cooling_effectiveness"],
            ambient_temp=env_data["temperature"],
            dt=self.tick_seconds
        )
        track_data = self._step_target_tracking(vibration=env_data["vibration"])
        
        return {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "session_id": self.current_session_id or "STANDBY",
            "environment": env_data,
            "computer": comp_data,
            "tracking": track_data,
            "scenario": self.current_scenario_name
        }

    async def _run_loop(self):
        while self.is_running:
            if not self.is_paused:
                state = self.generate_current_state()
                for cb in self._on_tick_callbacks:
                    try:
                        cb(state)
                    except Exception:
                        pass
            await asyncio.sleep(self.tick_seconds)
