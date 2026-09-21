"""
AI Model Loader and Verification Utility.
Project: SIH PS 26050 - High Altitude Anti-Drone System (DRDO)
"""

from typing import Dict, Any
from app.ai.detector import get_or_load_yolo


def get_model_info() -> Dict[str, Any]:
    """Returns metadata about the active AI inference engine."""
    model = get_or_load_yolo()
    if model is not None:
        return {
            "model_type": "Ultralytics YOLOv8 nano",
            "model_path": "yolov8n.pt",
            "status": "LOADED",
            "device": str(getattr(model, "device", "CPU")),
            "note": "Prototype AI model — specialized drone training required for deployment."
        }
    return {
        "model_type": "Synthetic Simulated Vision Engine",
        "model_path": "N/A (Simulation Mode)",
        "status": "SIMULATED",
        "device": "CPU Emulation",
        "note": "Prototype AI model — specialized drone training required for deployment."
    }
