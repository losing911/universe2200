"""
Shared Server Setup
"""
from fastapi import FastAPI
from api.broadcast_api import app as broadcast_app
from api.admin import router as admin_router
from core.universe_runtime import UniverseRuntime
from core.snapshot_manager import SnapshotManager
# Import other deps to build runtime...

def create_app(runtime: UniverseRuntime, snapshot_manager: SnapshotManager):
    """Factory to create the main app with mounted sub-apps/routers."""
    
    # Main App (Broadcast is root for now, or mount separately)
    # Actually, user asked for "API Layer".
    # Let's attach admin router to the broadcast app or create a new parent app.
    
    parent_app = FastAPI(title="Universe 2200 Server")
    
    # Mount Broadcast API
    # parent_app.mount("/public", broadcast_app) # Or just include router?
    # Broadcast app was separate. Let's include its routes if possible or mount it.
    parent_app.mount("/", broadcast_app) # Root is broadcast
    
    # Include Admin Router
    parent_app.include_router(admin_router)
    
    # Store runtime in state
    parent_app.state.runtime = runtime
    parent_app.state.snapshot_manager = snapshot_manager
    # Also set on broadcast_app state just in case
    broadcast_app.state.runtime = runtime
    
    return parent_app
