"""
System Health Engine evaluating multidimensional telemetry to determine operational status.
Project: SIH PS 26050 - High Altitude Anti-Drone System (DRDO)
"""

from typing import Dict, Any, List, Tuple
from app.core.config import settings


class HealthEngine:
    def __init__(self):
        self.last_status = "NORMAL"

    def evaluate(self, env_data: Dict[str, Any], comp_data: Dict[str, Any], tracking_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Derives real-time system health from coupled physical and compute parameters.
        Returns:
            status: "NORMAL" | "WARNING" | "DEGRADED" | "CRITICAL"
            score: int (0 to 100)
            reasons: List[str] explaining the status
        """
        reasons: List[str] = []
        score = 100

        cpu_temp = comp_data.get("cpu_temperature", 50.0)
        cpu_usage = comp_data.get("cpu_usage", 40.0)
        ai_fps = comp_data.get("fps", 25.0)
        ai_latency = comp_data.get("ai_latency", 40.0)
        vibration = env_data.get("vibration", 0.05)
        cooling = env_data.get("cooling_effectiveness", 95.0)
        track_conf = tracking_data.get("confidence", 0.90)

        critical_flags = 0
        warning_flags = 0

        # 1. Thermal check
        if cpu_temp >= settings.CPU_TEMP_CRIT:
            critical_flags += 1
            score -= 35
            reasons.append(f"CPU temperature critical ({cpu_temp}°C >= {settings.CPU_TEMP_CRIT}°C) — severe thermal throttling risk")
        elif cpu_temp >= settings.CPU_TEMP_WARN:
            warning_flags += 1
            score -= 15
            reasons.append(f"CPU temperature elevated ({cpu_temp}°C >= {settings.CPU_TEMP_WARN}°C) due to low air cooling ({cooling}%)")

        # 2. Compute Load check
        if cpu_usage >= settings.CPU_USAGE_CRIT:
            critical_flags += 1
            score -= 25
            reasons.append(f"CPU utilization saturated ({cpu_usage}%) — processing bottlenecks occurring")
        elif cpu_usage >= settings.CPU_USAGE_WARN:
            warning_flags += 1
            score -= 10
            reasons.append(f"High CPU workload ({cpu_usage}%) approaching capacity limits")

        # 3. AI Performance check
        if ai_fps <= settings.FPS_CRIT or ai_latency >= settings.LATENCY_CRIT_MS:
            critical_flags += 1
            score -= 30
            reasons.append(f"AI inference severely degraded (FPS: {ai_fps}, Latency: {ai_latency}ms)")
        elif ai_fps <= settings.FPS_WARN or ai_latency >= settings.LATENCY_WARN_MS:
            warning_flags += 1
            score -= 12
            reasons.append(f"AI processing latency increased ({ai_latency}ms) — frame rate reduced to {ai_fps} FPS")

        # 4. Vibration / Optical stability check
        if vibration >= settings.VIBRATION_CRIT:
            critical_flags += 1
            score -= 20
            reasons.append(f"Severe mechanical vibration ({vibration:.2f}) causing sensor destabilization")
        elif vibration >= settings.VIBRATION_WARN:
            warning_flags += 1
            score -= 10
            reasons.append(f"Elevated vibration disturbance ({vibration:.2f}) impacting tracking steadiness")

        # 5. Tracking confidence check
        if track_conf < 0.40:
            warning_flags += 1
            score -= 15
            reasons.append(f"Target optical lock degraded (Confidence: {int(track_conf * 100)}%)")

        # 6. Environmental Cooling check
        if cooling < 55.0:
            score -= 10
            reasons.append(f"High-altitude air density reduced thermal cooling effectiveness to {cooling}%")

        # Determine overall state
        score = max(5, min(100, score))

        if critical_flags > 0:
            status = "CRITICAL"
        elif warning_flags >= 2 or score < 60:
            status = "DEGRADED"
        elif warning_flags == 1 or score < 85:
            status = "WARNING"
        else:
            status = "NORMAL"

        if not reasons:
            reasons.append("All physical, atmospheric, compute, and tracking systems operating within nominal parameters.")

        self.last_status = status
        return {
            "status": status,
            "score": score,
            "reasons": reasons
        }
