import time
from fastapi import APIRouter, Query, Response
from fastapi.responses import StreamingResponse
from typing import Optional, List
from app.ai.detector import ai_detector
from app.ai.model_loader import get_model_info
from app.database.database import SessionLocal
from app.database.repositories import SystemRepository

router = APIRouter()


@router.get("/detections/latest")
def get_latest_detections(session_id: Optional[str] = Query(None)):
    with SessionLocal() as db:
        repo = SystemRepository(db)
        dets = repo.get_latest_detections(session_id, limit=1)
        if dets:
            d = dets[0]
            return {
                "id": d.id,
                "session_id": d.session_id,
                "timestamp": d.timestamp.isoformat() + "Z",
                "class_name": d.class_name,
                "confidence": d.confidence,
                "x": d.x,
                "y": d.y,
                "width": d.width,
                "height": d.height,
                "center_x": d.center_x,
                "center_y": d.center_y,
                "tracking_id": d.tracking_id,
                "fps": d.fps,
                "inference_latency": d.inference_latency
            }
    # Fallback to current instantaneous detection
    _, current_dets, meta = ai_detector.process_frame()
    return {
        "instantaneous": True,
        "detections": current_dets,
        "meta": meta
    }


@router.get("/detections/history")
def get_detections_history(session_id: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=500)):
    with SessionLocal() as db:
        repo = SystemRepository(db)
        records = repo.get_latest_detections(session_id, limit=limit)
        return [
            {
                "id": d.id,
                "session_id": d.session_id,
                "timestamp": d.timestamp.isoformat() + "Z",
                "class_name": d.class_name,
                "confidence": d.confidence,
                "x": d.x,
                "y": d.y,
                "width": d.width,
                "height": d.height,
                "center_x": d.center_x,
                "center_y": d.center_y,
                "tracking_id": d.tracking_id,
                "fps": d.fps,
                "inference_latency": d.inference_latency
            }
            for d in reversed(records)
        ]


@router.post("/detection/camera/start")
def start_camera(camera_index: int = 0):
    success = ai_detector.start_camera(camera_index)
    return {
        "success": success,
        "mode": ai_detector.mode,
        "camera_index": camera_index,
        "message": "Live webcam connected" if success else "Camera unavailable, using simulated video generator"
    }


@router.post("/detection/camera/stop")
def stop_camera():
    ai_detector.stop_camera()
    return {
        "success": True,
        "mode": ai_detector.mode,
        "message": "Reverted to simulated AI mode"
    }


@router.get("/ai/info")
def get_ai_info():
    return get_model_info()


def gen_video_frames():
    while True:
        frame_bytes = ai_detector.get_jpeg_frame()
        if frame_bytes:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        time.sleep(0.04)  # ~25 FPS stream


@router.get("/detection/video_feed")
def video_feed():
    """Live MJPEG video stream with bounding boxes and HUD crosshairs."""
    return StreamingResponse(
        gen_video_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )
