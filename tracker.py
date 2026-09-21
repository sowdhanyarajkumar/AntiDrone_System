"""
Software Pan-Tilt Tracking Solver
Project: SIH PS 26050 - High Altitude Anti-Drone System (DRDO)

NOTE / DISCLAIMER:
This is a software-only calculation that maps image-plane optical errors to simulated servo angles.
No physical servos or actuators are controlled.
"""

import math
from typing import Dict, Any, Optional


class SoftwareTracker:
    def __init__(self, frame_width: int = 640, frame_height: int = 480):
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.center_x = frame_width / 2.0  # 320.0
        self.center_y = frame_height / 2.0  # 240.0
        self.max_pan_deflection = 45.0  # +/- 45 deg from 90 deg neutral
        self.max_tilt_deflection = 35.0  # +/- 35 deg from 90 deg neutral

    def solve(self, target_x: float, target_y: float, confidence: float, vibration: float = 0.05) -> Dict[str, Any]:
        """
        Calculates error offsets and pan/tilt servo angles.
        """
        error_x = target_x - self.center_x
        error_y = target_y - self.center_y

        # Pan angle: Positive error_x (target to right) increases pan angle > 90°
        # Tilt angle: Positive error_y (target down) decreases tilt angle < 90°
        pan_angle = round(90.0 + (error_x / (self.frame_width / 2.0)) * self.max_pan_deflection, 1)
        tilt_angle = round(90.0 - (error_y / (self.frame_height / 2.0)) * self.max_tilt_deflection, 1)
        
        # Clamp angles to standard 0-180 degree servo sweep
        pan_angle = max(0.0, min(180.0, pan_angle))
        tilt_angle = max(0.0, min(180.0, tilt_angle))

        # Optical tracking confidence calculation
        dist = math.sqrt(error_x**2 + error_y**2)
        max_dist = math.sqrt(self.center_x**2 + self.center_y**2)
        centering_factor = max(0.0, 1.0 - (dist / max_dist))
        
        # Base tracking confidence combines detection confidence + boresight proximity
        track_conf = (confidence * 0.7) + (centering_factor * 0.3)
        
        # Vibration penalty
        if vibration > 0.35:
            track_conf -= (vibration - 0.35) * 0.40
        
        final_conf = round(max(0.05, min(0.99, track_conf)), 2)

        if final_conf > 0.65:
            status = "LOCKED"
        elif final_conf > 0.35:
            status = "ACQUIRING"
        else:
            status = "DEGRADED"

        return {
            "active": True,
            "target_x": round(target_x, 1),
            "target_y": round(target_y, 1),
            "image_center_x": self.center_x,
            "image_center_y": self.center_y,
            "error_x": round(error_x, 1),
            "error_y": round(error_y, 1),
            "pan_angle": pan_angle,
            "tilt_angle": tilt_angle,
            "confidence": final_conf,
            "status": status
        }
