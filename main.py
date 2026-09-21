"""
FastAPI Application Entrypoint
Project: SIH PS 26050 - High Altitude Anti-Drone System (DRDO)
"""

import json
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.websocket_manager import ws_manager
from app.database.database import init_db
from app.services.simulation_service import simulation_service
from app.api.routes import (
    health,
    telemetry,
    detection,
    tracking,
    environment,
    events,
    sessions,
    analysis,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print(f"[{settings.PROJECT_NAME}] Starting up...")
    init_db()
    print("[Database] SQLite database initialized at data/system.db (WAL mode)")
    yield
    # Shutdown
    print(f"[{settings.PROJECT_NAME}] Shutting down...")
    simulation_service.reset()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(health.router, prefix=settings.API_V1_PREFIX, tags=["Health"])
app.include_router(telemetry.router, prefix=settings.API_V1_PREFIX, tags=["Telemetry"])
app.include_router(detection.router, prefix=settings.API_V1_PREFIX, tags=["Detection"])
app.include_router(tracking.router, prefix=settings.API_V1_PREFIX, tags=["Tracking"])
app.include_router(environment.router, prefix=settings.API_V1_PREFIX, tags=["Environment & Simulation"])
app.include_router(events.router, prefix=settings.API_V1_PREFIX, tags=["Events"])
app.include_router(sessions.router, prefix=settings.API_V1_PREFIX, tags=["Sessions"])
app.include_router(analysis.router, prefix=settings.API_V1_PREFIX, tags=["Analysis"])


# Real-time WebSocket Endpoint
@app.websocket("/ws/telemetry")
async def websocket_telemetry_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    # Immediately transmit instantaneous state upon connection
    initial_packet = simulation_service.current_state or {
        "type": "system",
        "status": "CONNECTED",
        "message": "Connected to Aeronex Anti-Drone Telemetry Broker",
        "session_id": simulation_service.current_session_id or "STANDBY"
    }
    await websocket.send_text(json.dumps(initial_packet))

    try:
        while True:
            # Keep connection alive and listen for client inbound commands (e.g. ping/heartbeat)
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                if payload.get("action") == "ping":
                    await websocket.send_text(json.dumps({"type": "pong"}))
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        ws_manager.disconnect(websocket)


# Mount built frontend static files (for single-service deployment on Railway)
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Determine static frontend directory (prefer backend/app/static, fallback to ../../frontend/dist)
static_candidates = [
    os.path.abspath(os.path.join(os.path.dirname(__file__), "static")),
    os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")),
    os.path.abspath("frontend/dist"),
]

frontend_dist = next((p for p in static_candidates if os.path.isdir(p) and os.path.isfile(os.path.join(p, "index.html"))), None)

if frontend_dist:
    assets_dir = os.path.join(frontend_dist, "assets")
    if os.path.isdir(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/")
    async def serve_root():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        if full_path.startswith("api") or full_path.startswith("ws"):
            return None
        candidate = os.path.join(frontend_dist, full_path)
        if os.path.isfile(candidate):
            return FileResponse(candidate)
        return FileResponse(os.path.join(frontend_dist, "index.html"))


