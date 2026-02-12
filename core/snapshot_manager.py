"""
Snapshot Manager for Universe 2200

Handles persistence of simulation state via periodic snapshots.
Ensures atomic writes and deterministic loading for production safety.
"""

import json
import os
import glob
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

logger = logging.getLogger("SnapshotManager")

class SnapshotManager:
    """
    Manages saving and loading of simulation snapshots.
    """
    
    def __init__(self, data_dir: str = "data/snapshots"):
        """
        Initialize SnapshotManager.
        
        Args:
            data_dir: Directory to store snapshot files
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def save_snapshot(self, 
                     tick: int, 
                     world_state: Dict[str, Any], 
                     top_entities: List[Dict[str, Any]],
                     influence_distribution: Dict[str, float]) -> str:
        """
        Save a snapshot of the current simulation state.
        
        Args:
            tick: Current tick number
            world_state: Dictionary of world metrics
            top_entities: List of top entity objects/summaries
            influence_distribution: Dictionary of influence scores
            
        Returns:
            Path to the saved snapshot file
        """
        filename = f"tick_{tick:06d}.json"
        filepath = self.data_dir / filename
        
        # Construct snapshot data structure
        snapshot_data = {
            "tick": tick,
            "timestamp": world_state.get("current_date", ""),
            "metrics": world_state,
            "unrest": world_state.get("public_unrest", 0.0),
            "top_entities": top_entities,
            "influence_distribution": influence_distribution,
            "meta": {
                "version": "1.0",
                "saved_at": str(filepath)
            }
        }
        
        # Atomic Write: Write to temp file then rename
        temp_path = filepath.with_suffix('.tmp')
        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(snapshot_data, f, indent=2, sort_keys=True)
                
            # Rename to final filename (atomic operation on POSIX, usually safe on Windows)
            if filepath.exists():
                os.remove(filepath) # Ensure overwrite on Windows
            os.rename(temp_path, filepath)
            
            logger.info(f"Snapshot saved: {filepath}")
            return str(filepath)
            
        except Exception as e:
            logger.error(f"Failed to save snapshot {tick}: {e}")
            if temp_path.exists():
                os.remove(temp_path)
            raise e

    def load_latest_snapshot(self) -> Optional[Dict[str, Any]]:
        """
        Load the most recent snapshot file.
        
        Returns:
            Snapshot dictionary or None if no snapshots exist.
        """
        files = glob.glob(str(self.data_dir / "tick_*.json"))
        if not files:
            logger.info("No snapshots found.")
            return None
            
        # Sort by tick number (filename) ensures determinism
        # Filename format is tick_XXXXXX.json, so alphabetical sort works for numbers
        latest_file = max(files, key=os.path.getctime) 
        # Actually, best to sort by name to rely on ID not FS timestamps
        latest_file = sorted(files)[-1]
        
        try:
            with open(latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded snapshot from {latest_file} (Tick {data.get('tick')})")
                return data
        except Exception as e:
            logger.error(f"Failed to load snapshot {latest_file}: {e}")
            return None

    def resume_from_snapshot(self) -> Tuple[int, Dict[str, Any]]:
        """
        Load latest snapshot to resume simulation.
        
        Returns:
            Tuple of (tick_number, snapshot_data)
        """
        data = self.load_latest_snapshot()
        if not data:
            return 0, {}
            
        return data.get("tick", 0), data

    def cleanup_old_snapshots(self, keep_last: int = 5):
        """
        Remove old snapshots to save space, keeping only the N most recent.
        """
        files = sorted(glob.glob(str(self.data_dir / "tick_*.json")))
        if len(files) <= keep_last:
            return
            
        to_delete = files[:-keep_last]
        for f in to_delete:
            try:
                os.remove(f)
                logger.debug(f"Deleted old snapshot: {f}")
            except OSError as e:
                logger.warning(f"Error deleting {f}: {e}")
