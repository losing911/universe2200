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
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
            
            # Run Scheduler/Runtime Tick
            # DailyScheduler.run_daily_tick advances date and runs runtime.run_tick
            step_result = scheduler.run_daily_tick() # This persists state too
            
            # Gather Data for Public Cache
            content = step_result.get("content", {})
            timestamp_str = step_result["date"].strftime('%Y-%m-%d')
            
            # 1. News
            if content.get("news"):
                write_public_file("public_news.json", {
                    "status": "live",
                    "timestamp": timestamp_str,
                    "tick": step_result["tick"],
                    "data": content["news"]
                })
                
            # 2. Social (Dual Platform)
            
            try:
                # Use Real Simulation Data if available
                if runtime.social_network:
                    # Get global feed from the population engine results
                    # We can use the same feed for both X and Insta for now, 
                    # or filter by content type if we had it. 
                    # For MVP, both get the same "Global Feed".
                    
                    global_feed = runtime.social_network.get_global_feed(limit=20)
                    
                    # Write to X (Twitter-like)
                    write_public_file("public_social_x.json", {
                        "status": "live",
                        "timestamp": timestamp_str,
                        "tick": step_result["tick"],
                        "data": global_feed
                    })
                    
                    # Write to Insta (Visuals) - In future, filter for 'image' types
                    write_public_file("public_social_insta.json", {
                        "status": "live",
                        "timestamp": timestamp_str,
                        "tick": step_result["tick"],
                        "data": global_feed 
                    })
                    
                    snapshot_social_x = global_feed
                    snapshot_social_insta = global_feed
                    
                elif runtime.content_pipeline and runtime.content_pipeline.social_gen:
                    # FALLBACK to Random Generator if SocialNetwork is missing
                    metrics = scheduler.get_current_state()['metrics']
                    news_items = content.get("news", [])
                    social_gen = runtime.content_pipeline.social_gen
                    
                    # Store for snapshot
                    snapshot_social_x = x_feed["posts"]
                    snapshot_social_insta = insta_feed["posts"]
                else:
                    write_public_file("public_social_x.json", {
                        "status": "waiting_for_pipeline",
                        "timestamp": timestamp_str,
                        "tick": step_result["tick"],
                        "data": []
                    })
                    write_public_file("public_social_insta.json", {
                        "status": "waiting_for_pipeline",
                        "timestamp": timestamp_str,
                        "tick": step_result["tick"],
                        "data": []
                    })
                    snapshot_social_x = []
                    snapshot_social_insta = []
            except Exception as e:
                logger.error(f"Social generation failed: {e}", exc_info=True)
                # Write empty files so API doesn't break
                write_public_file("public_social_x.json", {
                    "status": "error",
                    "error": str(e),
                    "timestamp": timestamp_str,
                    "tick": step_result["tick"],
                    "data": []
                })
                write_public_file("public_social_insta.json", {
                    "status": "error",
                    "error": str(e),
                    "timestamp": timestamp_str,
                    "tick": step_result["tick"],
                    "data": []
                })
                snapshot_social_x = []
                snapshot_social_insta = []

            # Construct Public Data
            current_state = scheduler.get_current_state()
            
            # Metrics
            metrics_data = current_state['metrics']
            write_public_file("public_metrics.json", {
                "status": "live",
                "timestamp": timestamp_str,
                "tick": step_result["tick"],
                "data": metrics_data
            })
            
            # Snapshot Update (Full Public State)
            snapshot_data = {
                "tick": runtime.tick_count,
                "date": timestamp_str,
                "metrics": metrics_data,
                "news": content.get("news", []),
                "social_x": snapshot_social_x,
                "social_insta": snapshot_social_insta,
                "status": "running"
            }
            write_public_file("public_snapshot.json", snapshot_data)
            
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
