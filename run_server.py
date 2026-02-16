"""
Universe 2200 - Integrated Server Runner

Starts the Simulation Engine and API Layer in a single process.
Usage: python run_server.py
"""

import uvicorn
import logging
from simulation.scheduler import DailyScheduler
from core.snapshot_manager import SnapshotManager
from server import create_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ServerRunner")

def main():
    logger.info("🚀 Starting Universe 2200 Server...")
    
    # 1. Initialize Simulation Engine
    scheduler = DailyScheduler()
    scheduler.initialize()
    
    # 2. Get Runtime Reference
    # Scheduler creates runtime in .initialize()
    if not scheduler.runtime:
        logger.error("Failed to initialize runtime!")
        return
        
    runtime = scheduler.runtime
    
    # 3. Create Snapshot Manager
    snapshot_manager = SnapshotManager()
    
    # 4. Create FastAPI App
    app = create_app(runtime, snapshot_manager)
    
    # 5. Run Server
    # Note: access_log=False to reduce noise from high-frequency polling
    logger.info("📡 API listening on http://localhost:8000")
    logger.info("🔧 Admin Dashboard at http://localhost:8000/admin")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

if __name__ == "__main__":
    main()
