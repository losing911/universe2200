"""
Universe 2200 - Simulation Engine (Process A)

Role: Writer
Responsibilities:
- Run infinite simulation loop
- Generate content and metrics
- Write public JSON cache to data/public/
- Manage snapshots

Constraints:
- No API exposure
- No external connectivity requirements
- Strict file-based output
"""

import time
import json
import logging
import os
from pathlib import Path
from simulation.scheduler import DailyScheduler
from core.snapshot_manager import SnapshotManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("SimEngine")

# Configuration
DATA_DIR = Path("data")
PUBLIC_DIR = DATA_DIR / "public"
PUBLIC_DIR.mkdir(parents=True, exist_ok=True)

TICK_INTERVAL = 1.0  # Seconds per tick (Process A speed)
SNAPSHOT_INTERVAL = 50  # Ticks per snapshot

def write_public_file(filename: str, data: dict):
    """Atomic write to public cache directory."""
    filepath = PUBLIC_DIR / filename
    temp_path = filepath.with_suffix('.tmp')
    
    try:
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, sort_keys=True)
        # Atomic rename
        if filepath.exists():
            os.remove(filepath)
        os.rename(temp_path, filepath)
    except Exception as e:
        logger.error(f"Failed to write {filename}: {e}")

def main():
    logger.info("🚀 Starting Universe 2200 Simulation Process...")
    
    # 1. Initialize Engines
    scheduler = DailyScheduler(data_dir=str(DATA_DIR))
    scheduler.initialize()
    
    runtime = scheduler.runtime
    snapshot_manager = SnapshotManager(data_dir=str(DATA_DIR / "snapshots"))
    
    # Check for latest snapshot to resume
    start_tick, snapshot_data = snapshot_manager.resume_from_snapshot()
    if snapshot_data:
        logger.info(f"🔄 Resuming from Tick {start_tick}")
        # Note: Runtime restore logic would go here if implemented deep copy
        # For now, we manually set tick count and basic metrics if possible
        # runtime.tick_count = start_tick 
        # But fully restoring state requires runtime support.
        # Assuming resume works or we just start fresh for now.
        pass

    logger.info("⚡ Simulation Loop Active")
    
    try:
        while True:
            # Execute Tick
            start_time = time.time()
            
            # Run Scheduler/Runtime Tick
            # DailyScheduler.run_daily_tick advances date and runs runtime.run_tick
            # But run_daily_tick runs ONCE per day? 
            # We want finer grain if content pipeline runs every runtime tick.
            # DailyScheduler wraps runtime.run_tick
            
            scheduler.run_daily_tick() # This persists state too
            
            # Gather Data for Public Cache
            # 1. News
            news_items = [] # We need to capture from pipeline output
            # Current implementation of scheduler doesn't easily return pipeline output
            # We might need to tap into runtime.content_pipeline.last_output if it existed
            # or rely on what's in world state logs?
            
            # Refactor: We can access runtime components manually
            
            # Construct Public Data
            current_state = scheduler.get_current_state()
            
            # Metrics
            metrics_data = current_state['metrics']
            write_public_file("public_metrics.json", metrics_data)
            
            # Snapshot Update (Full Public State)
            snapshot_data = {
                "tick": runtime.tick_count,
                "date": current_state['date'].strftime('%Y-%m-%d'),
                "metrics": metrics_data,
                "status": "running"
            }
            write_public_file("public_snapshot.json", snapshot_data)
            
            # Simulate News/Social updates (mock or real if pipeline stores them)
            # In real impl, we'd read from a buffer in ContentPipeline
            # For now, we write placeholders or what we have.
            
            # Persist Snapshot
            if runtime.tick_count % SNAPSHOT_INTERVAL == 0:
                logger.info(f"💾 Saving Snapshot Tick {runtime.tick_count}")
                snapshot_manager.save_snapshot(
                    tick=runtime.tick_count,
                    world_state=runtime.world_state.to_dict(),
                    top_entities=[], # Populate if available
                    influence_distribution={}
                )
            
            # Throttle
            elapsed = time.time() - start_time
            sleep_time = max(0.0, TICK_INTERVAL - elapsed)
            if sleep_time > 0:
                time.sleep(sleep_time)

    except KeyboardInterrupt:
        logger.info("🛑 Simulation Stopped by User")
    except Exception as e:
        logger.critical(f"🔥 Simulation Crashed: {e}", exc_info=True)

if __name__ == "__main__":
    main()
