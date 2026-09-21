from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from app.services.simulation_service import simulation_service
from app.simulation.disturbances import SCENARIOS

router = APIRouter()


class SimulationConfigReq(BaseModel):
    altitude: Optional[float] = Field(None, ge=0.0, le=6000.0)
    vibration: Optional[float] = Field(None, ge=0.0, le=1.0)
    cpu_load: Optional[float] = Field(None, ge=0.0, le=1.0)
    ai_load: Optional[float] = Field(None, ge=0.0, le=1.0)
    tick_seconds: Optional[float] = Field(None, ge=0.2, le=5.0)


class StartSessionReq(BaseModel):
    initial_altitude: float = 1000.0


@router.post("/simulation/start")
async def start_simulation(req: StartSessionReq = StartSessionReq()):
    session = simulation_service.start_session(initial_altitude=req.initial_altitude)
    return {
        "status": "started",
        "session": session
    }


@router.post("/simulation/pause")
async def pause_simulation():
    success = simulation_service.pause_session()
    return {"status": "paused" if success else "failed"}


@router.post("/simulation/resume")
async def resume_simulation():
    success = simulation_service.resume_session()
    return {"status": "resumed" if success else "failed"}


@router.post("/simulation/stop")
async def stop_simulation():
    session = simulation_service.stop_session()
    return {
        "status": "stopped",
        "session": session
    }


@router.post("/simulation/reset")
async def reset_simulation():
    simulation_service.reset()
    return {"status": "reset"}


@router.post("/simulation/config")
async def update_simulation_config(cfg: SimulationConfigReq):
    if cfg.altitude is not None:
        simulation_service.engine.set_altitude(cfg.altitude)
    if cfg.vibration is not None:
        simulation_service.engine.set_vibration(cfg.vibration)
    if cfg.cpu_load is not None:
        simulation_service.engine.set_compute_load(cfg.cpu_load)
    if cfg.ai_load is not None:
        simulation_service.engine.set_ai_load(cfg.ai_load)
    if cfg.tick_seconds is not None:
        simulation_service.engine.tick_seconds = cfg.tick_seconds

    return {
        "status": "updated",
        "current_altitude": simulation_service.engine.env_sim.current_altitude,
        "vibration_disturbance": simulation_service.engine.env_sim.vibration_disturbance,
        "user_cpu_load": simulation_service.engine.comp_sim.user_cpu_load_factor,
        "ai_load": simulation_service.engine.comp_sim.ai_load_factor
    }


@router.get("/simulation/scenarios")
def list_scenarios():
    return SCENARIOS


@router.post("/simulation/scenario/{name}")
def apply_scenario(name: str):
    success = simulation_service.engine.apply_scenario(name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Scenario '{name}' not found")
    return {
        "status": "applied",
        "scenario": name,
        "details": SCENARIOS[name]
    }
