"""
Test Snapshot Manager
"""
import os
import shutil
from core.snapshot_manager import SnapshotManager

def test_snapshot_manager():
    print("=== Testing Snapshot Manager ===\n")
    
    test_dir = "data/test_snapshots"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    manager = SnapshotManager(data_dir=test_dir)
    
    # 1. Test Save
    print("1. Testing Save Snapshot:")
    tick = 100
    world_state = {"public_unrest": 0.5, "current_date": "2200-01-01"}
    top_entities = [{"id": "user_1", "score": 10}]
    influence = {"user_1": 10.0}
    
    path = manager.save_snapshot(tick, world_state, top_entities, influence)
    print(f"Saved to: {path}")
    assert os.path.exists(path)
    
    # 2. Test Load Latest
    print("\n2. Testing Load Latest:")
    # Save a newer one
    manager.save_snapshot(150, world_state, top_entities, influence)
    
    latest = manager.load_latest_snapshot()
    print(f"Loaded Tick: {latest['tick']}")
    assert latest['tick'] == 150
    assert latest['unrest'] == 0.5
    
    # 3. Test Resume
    print("\n3. Testing Resume:")
    resume_tick, resume_data = manager.resume_from_snapshot()
    print(f"Resume Tick: {resume_tick}")
    assert resume_tick == 150
    
    # 4. Cleanup
    print("\n4. Cleanup Test (Keep last 1):")
    manager.cleanup_old_snapshots(keep_last=1)
    files = os.listdir(test_dir)
    print(f"Files after cleanup: {files}")
    assert len(files) == 1
    assert "tick_000150.json" in files[0]
    
    # Clean up test dir
    shutil.rmtree(test_dir)
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_snapshot_manager()
