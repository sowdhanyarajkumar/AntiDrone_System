import pytest
from app.ai.tracker import SoftwareTracker


def test_tracker_boresight_center():
    tracker = SoftwareTracker(frame_width=640, frame_height=480)
    # Target right at center (320, 240)
    res = tracker.solve(target_x=320.0, target_y=240.0, confidence=0.95)
    
    assert res["error_x"] == 0.0
    assert res["error_y"] == 0.0
    assert res["pan_angle"] == 90.0
    assert res["tilt_angle"] == 90.0
    assert res["status"] == "LOCKED"


def test_tracker_offset_quadrants():
    tracker = SoftwareTracker(frame_width=640, frame_height=480)
    
    # Target right and down
    res = tracker.solve(target_x=480.0, target_y=360.0, confidence=0.90)
    assert res["error_x"] > 0
    assert res["error_y"] > 0
    assert res["pan_angle"] > 90.0  # Pan deflected to right
    assert res["tilt_angle"] < 90.0  # Tilt deflected downward
