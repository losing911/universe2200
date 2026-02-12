"""
Admin Control Panel for Universe 2200

Internal API for managing the simulation state.
Requires Basic Authentication.
Cleanly separated from public broadcast API.
"""

import os
import time
import psutil
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

# Configuration
ADMIN_USER = os.getenv("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "universe2200")

# Router
router = APIRouter(prefix="/admin", tags=["Admin Control"])
security = HTTPBasic()
logger = logging.getLogger("AdminAPI")
templates = Jinja2Templates(directory="templates")

# Models
class TickSpeedRequest(BaseModel):
    seconds_per_tick: float

class SnapshotRestoreRequest(BaseModel):
    tick: int

# Auth Dependency
def verify_admin(credentials: HTTPBasicCredentials = Depends(security)):
    """Verify Basic Auth credentials."""
    is_user_ok = credentials.username == ADMIN_USER
    is_pass_ok = credentials.password == ADMIN_PASSWORD
    
    if not (is_user_ok and is_pass_ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Helpers
def get_runtime(request: Request):
    """Retrieve runtime instance from app state."""
    if not hasattr(request.app.state, "runtime"):
        raise HTTPException(status_code=503, detail="Simulation runtime not initialized")
    return request.app.state.runtime

def get_snapshot_manager(request: Request):
    """Retrieve snapshot manager from app state."""
    # Assuming runtime has access or app.state has it
    if hasattr(request.app.state, "snapshot_manager"):
        return request.app.state.snapshot_manager
    # Fallback: try to find it on runtime
    runtime = get_runtime(request)
    if hasattr(runtime, "snapshot_manager"): # If we added it to runtime
        return runtime.snapshot_manager
    # Fallback 2: Instantiate new (not ideal for sharing state but basic works for listing)
    from core.snapshot_manager import SnapshotManager
    return SnapshotManager()

# --- Endpoints ---

@router.get("/", response_class=HTMLResponse, dependencies=[Depends(verify_admin)])
async def admin_dashboard(request: Request):
    """Serve the admin dashboard HTML."""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/status", dependencies=[Depends(verify_admin)])
async def get_status(request: Request):
    """Get current simulation status."""
    runtime = get_runtime(request)
    
    return {
        "tick": runtime.tick_count,
        "running": runtime.running,
        "mode": runtime.config.mode,
        "tick_speed": runtime.config.tick_interval_seconds,
        "metrics": {
            "unrest": runtime.world_state.get_metric("public_unrest"),
            "noise": runtime.world_state.get_metric("information_noise"),
            "surveillance": runtime.world_state.get_metric("surveillance_level")
        }
    }

@router.post("/pause", dependencies=[Depends(verify_admin)])
async def pause_simulation(request: Request):
    """Pause the simulation loop."""
    runtime = get_runtime(request)
    if not runtime.running:
        return {"status": "already_paused"}
    
    runtime.running = False # This stops the loop in UniverseRuntime
    # runtime.stop() joins the thread, which might block API if called from same loop? 
    # But usually stop() signals flag then joins.
    # For safety in async, we just set flag or call non-blocking stop request.
    # runtime.stop() in current impl joins. 
    # Better to just set flag and let it spin down? 
    # For now, we'll try standard stop() but maybe in background task if it blocks.
    # Actually runtime.stop() joins for 5s.
    runtime.stop()
    return {"status": "paused", "tick": runtime.tick_count}

@router.post("/resume", dependencies=[Depends(verify_admin)])
async def resume_simulation(request: Request):
    """Resume the simulation loop."""
    runtime = get_runtime(request)
    if runtime.running:
        return {"status": "already_running"}
    
    runtime.start()
    return {"status": "resumed", "tick": runtime.tick_count}

@router.post("/set_tick_speed", dependencies=[Depends(verify_admin)])
async def set_tick_speed(request: Request, body: TickSpeedRequest):
    """Update simulation speed."""
    runtime = get_runtime(request)
    runtime.config.tick_interval_seconds = body.seconds_per_tick
    return {
        "status": "updated", 
        "tick_interval_seconds": runtime.config.tick_interval_seconds
    }

@router.post("/force_snapshot", dependencies=[Depends(verify_admin)])
async def force_snapshot(request: Request):
    """Trigger an immediate snapshot save."""
    runtime = get_runtime(request)
    manager = get_snapshot_manager(request)
    
    # We need to gather data similar to how runtime does it?
    # Or runtime should have a method `save_snapshot`?
    # Ideally runtime handles this.
    # If not, we construct it here manually (risky).
    
    # Check if runtime has logic. If not, implement minimal save here.
    # We need top entities... runtime might not track them easily publicly.
    # Let's try to access activity_pipeline population if possible.
    
    top_entities = []
    if hasattr(runtime, 'activity_pipeline') and hasattr(runtime.activity_pipeline, 'population_engine'):
        # Just top 5 by influence
        pop = runtime.activity_pipeline.population_engine.population
        sorted_pop = sorted(pop, key=lambda u: getattr(u, 'influence_score', 0), reverse=True)[:5]
        top_entities = [{"id": u.user_id, "score": u.influence_score} for u in sorted_pop]
        
    influence_dist = {} # Placeholder if not easy to get
    
    path = manager.save_snapshot(
        tick=runtime.tick_count,
        world_state=runtime.world_state.to_dict(),
        top_entities=top_entities,
        influence_distribution=influence_dist
    )
    
    return {"status": "snapshot_created", "path": path}

@router.get("/snapshots", dependencies=[Depends(verify_admin)])
async def list_snapshots(request: Request):
    """List available snapshots."""
    manager = get_snapshot_manager(request)
    # We need to access manager's dir
    # manager.data_dir is Path
    files = sorted(manager.data_dir.glob("tick_*.json"))
    return {
        "count": len(files),
        "snapshots": [f.name for f in files]
    }

@router.post("/restore_snapshot", dependencies=[Depends(verify_admin)])
async def restore_snapshot(request: Request, body: SnapshotRestoreRequest):
    """
    Restore simulation state from a snapshot.
    Note: This is a complex operation that might require restarting the runtime.
    """
    # For now, return 501 Not Implemented or try basic state reload
    raise HTTPException(status_code=501, detail="Hot restore not yet implemented. Please restart server with resume flag.")

@router.get("/system_health", dependencies=[Depends(verify_admin)])
async def system_health(request: Request):
    """Monitor system resource usage."""
    process = psutil.Process(os.getpid())
    
    return {
        "cpu_percent": process.cpu_percent(),
        "memory_info": process.memory_info()._asdict(),
        "uptime_seconds": time.time() - process.create_time(),
        "threads": process.num_threads()
    }
