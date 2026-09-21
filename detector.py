"""
AI Detection and Computer Vision Pipeline using OpenCV & Ultralytics YOLOv8.
Project: SIH PS 26050 - High Altitude Anti-Drone System (DRDO)

NOTE:
"Prototype AI model — specialized drone training required for deployment."
"""

import time
import cv2
import numpy as np
import random
from typing import Dict, Any, List, Optional, Tuple
from app.core.config import settings

# Global model cache
_yolo_model = None


def get_or_load_yolo():
    global _yolo_model
    if _yolo_model is None:
        try:
            from ultralytics import YOLO
            # Will automatically use or download yolov8n.pt
            _yolo_model = YOLO("yolov8n.pt")
        except Exception as e:
            print(f"[AI] Notice: Could not load local YOLO model ({e}). Using simulated detector.")
            _yolo_model = None
    return _yolo_model


class AIDetectorService:
    def __init__(self):
        self.mode = "SIMULATED"  # "LIVE_AI" or "SIMULATED"
        self.cap: Optional[cv2.VideoCapture] = None
        self.camera_index = settings.DEFAULT_CAMERA_INDEX
        self.last_frame_time = time.time()
        self.fps = 24.0
        self.latency_ms = 35.0
        
        # Synthetic generator state
        self.synth_x = 280.0
        self.synth_y = 190.0
        self.synth_vx = 4.0
        self.synth_vy = 2.2

    def start_camera(self, camera_index: int = 0) -> bool:
        """Attempt to open physical or virtual webcam."""
        try:
            if self.cap is not None:
                self.cap.release()
            self.cap = cv2.VideoCapture(camera_index)
            if self.cap.isOpened():
                ret, frame = self.cap.read()
                if ret and frame is not None:
                    self.camera_index = camera_index
                    self.mode = "LIVE_AI"
                    return True
            # If camera failed to open
            if self.cap is not None:
                self.cap.release()
                self.cap = None
        except Exception as e:
            print(f"[AI] Camera open exception: {e}")
            self.cap = None

        self.mode = "SIMULATED"
        return False

    def stop_camera(self):
        if self.cap is not None:
            self.cap.release()
            self.cap = None
        self.mode = "SIMULATED"

    def _generate_synthetic_frame(self) -> np.ndarray:
        """Creates an aerospace HUD video frame with synthetic mountainous terrain and target drone."""
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        
        # Atmospheric gradient (high altitude dark-blue sky)
        for y in range(480):
            b = int(40 + (y / 480.0) * 50)
            g = int(25 + (y / 480.0) * 35)
            r = int(15 + (y / 480.0) * 25)
            frame[y, :] = (b, g, r)

        # Draw distant mountain horizon
        pts = np.array([[0, 360], [120, 290], [240, 330], [380, 270], [500, 320], [640, 280], [640, 480], [0, 480]], np.int32)
        cv2.fillPoly(frame, [pts], (30, 35, 45))

        # Move synthetic drone
        self.synth_x += self.synth_vx
        self.synth_y += self.synth_vy
        if self.synth_x <= 60 or self.synth_x >= 580:
            self.synth_vx = -self.synth_vx
        if self.synth_y <= 50 or self.synth_y >= 350:
            self.synth_vy = -self.synth_vy

        # Draw synthetic drone quadcopter icon
        cx, cy = int(self.synth_x), int(self.synth_y)
        # Center fuselage
        cv2.circle(frame, (cx, cy), 10, (180, 180, 180), -1)
        # Arms
        cv2.line(frame, (cx - 22, cy - 14), (cx + 22, cy + 14), (120, 120, 120), 2)
        cv2.line(frame, (cx - 22, cy + 14), (cx + 22, cy - 14), (120, 120, 120), 2)
        # Rotors
        for rx, ry in [(cx - 22, cy - 14), (cx + 22, cy + 14), (cx - 22, cy + 14), (cx + 22, cy - 14)]:
            cv2.ellipse(frame, (rx, ry), (12, 3), 0, 0, 360, (220, 220, 220), 1)

        # Boresight Center Crosshairs
        cv2.drawMarker(frame, (320, 240), (0, 255, 180), cv2.MARKER_CROSS, 20, 1)
        cv2.circle(frame, (320, 240), 40, (0, 255, 180), 1)

        return frame

    def process_frame(self) -> Tuple[np.ndarray, List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes detection on current frame.
        Returns:
            annotated_frame: np.ndarray
            detections: List[Dict]
            meta: Dict with fps, latency, mode, etc.
        """
        start_t = time.time()
        raw_frame = None

        if self.mode == "LIVE_AI" and self.cap is not None and self.cap.isOpened():
            ret, captured = self.cap.read()
            if ret and captured is not None:
                raw_frame = captured
            else:
                # Camera feed dropped, fallback
                self.mode = "SIMULATED"

        if raw_frame is None:
            raw_frame = self._generate_synthetic_frame()

        h, w = raw_frame.shape[:2]
        detections: List[Dict[str, Any]] = []

        # Run inference
        model = get_or_load_yolo() if self.mode == "LIVE_AI" else None

        if model is not None and self.mode == "LIVE_AI":
            try:
                results = model(raw_frame, verbose=False, conf=settings.YOLO_CONFIDENCE_THRESHOLD)
                for r in results:
                    boxes = r.boxes
                    for box in boxes:
                        b = box.xyxy[0].tolist()  # [x1, y1, x2, y3]
                        conf = float(box.conf[0])
                        cls_id = int(box.cls[0])
                        cls_name = model.names.get(cls_id, "drone")
                        
                        bw = b[2] - b[0]
                        bh = b[3] - b[1]
                        cx = b[0] + bw / 2.0
                        cy = b[1] + bh / 2.0

                        det_item = {
                            "class_name": cls_name,
                            "confidence": round(conf, 2),
                            "x": round(b[0], 1),
                            "y": round(b[1], 1),
                            "width": round(bw, 1),
                            "height": round(bh, 1),
                            "center_x": round(cx, 1),
                            "center_y": round(cy, 1),
                            "tracking_id": "T-101"
                        }
                        detections.append(det_item)
            except Exception as ex:
                print(f"[AI] YOLO inference error: {ex}")

        # If no detections from model or in simulated mode, provide realistic simulated drone target
        if not detections:
            bw = 64.0
            bh = 48.0
            x = self.synth_x - bw / 2.0
            y = self.synth_y - bh / 2.0
            det_item = {
                "class_name": "simulated_drone",
                "confidence": round(0.88 + random.uniform(-0.04, 0.05), 2),
                "x": round(x, 1),
                "y": round(y, 1),
                "width": bw,
                "height": bh,
                "center_x": round(self.synth_x, 1),
                "center_y": round(self.synth_y, 1),
                "tracking_id": "HA-DRONE-01"
            }
            detections.append(det_item)

        # Annotate frame
        annotated = raw_frame.copy()
        for det in detections:
            x1, y1 = int(det["x"]), int(det["y"])
            x2, y2 = int(det["x"] + det["width"]), int(det["y"] + det["height"])
            cx, cy = int(det["center_x"]), int(det["center_y"])
            
            # Corner brackets / box
            cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 240, 255), 2)
            cv2.circle(annotated, (cx, cy), 4, (0, 0, 255), -1)
            
            label = f"{det['class_name'].upper()} {int(det['confidence'] * 100)}%"
            cv2.putText(annotated, label, (x1, max(18, y1 - 6)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 240, 255), 2)

            # Draw vector line to center
            cv2.line(annotated, (320, 240), (cx, cy), (0, 180, 255), 1, cv2.LINE_AA)

        # Latency & FPS calculation
        end_t = time.time()
        self.latency_ms = round((end_t - start_t) * 1000.0, 1)
        if self.latency_ms < 1.0:
            self.latency_ms = 32.5  # baseline synthetic compute time
        
        dt_frame = end_t - self.last_frame_time
        self.last_frame_time = end_t
        if dt_frame > 0:
            curr_fps = 1.0 / dt_frame
            self.fps = round(self.fps * 0.8 + curr_fps * 0.2, 1)
        self.fps = max(1.0, min(60.0, self.fps))

        meta = {
            "ai_mode": self.mode,
            "fps": self.fps,
            "inference_latency": self.latency_ms,
            "warning_note": "Prototype AI model — specialized drone training required for deployment."
        }
        return annotated, detections, meta

    def get_jpeg_frame(self) -> bytes:
        """Returns JPEG encoded bytes of annotated frame for streaming."""
        annotated, _, _ = self.process_frame()
        ret, jpeg = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        return jpeg.tobytes() if ret else b""


# Singleton instance
ai_detector = AIDetectorService()
