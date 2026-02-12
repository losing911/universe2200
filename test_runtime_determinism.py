"""
Test Universe Runtime Determinism
"""
from simulation.population_engine import PopulationEngine
from core.universe_runtime import UniverseRuntime
import json

def test_tick_determinism():
    print("--- Testing Runtime Tick Determinism ---")
    
    # Setup
    world_state = {"public_unrest": 0.5, "date": "2207-08-01"}
    posts = [
        {"id": "p1", "topic": "tech", "author_faction": "bio"},
        {"id": "p2", "topic": "politics", "author_faction": "synthetic"}
    ]
    
    engine = PopulationEngine(size=100, seed=42)
    
    # Run 1: with tick_seed=100
    print("Running with seed 100...")
    res1 = engine.generate_daily_activity(world_state, posts, tick_seed=100)
    
    # Run 2: with tick_seed=100 (should be identical)
    print("Running with seed 100 again...")
    res2 = engine.generate_daily_activity(world_state, posts, tick_seed=100)
    
    # Run 3: with tick_seed=101 (should differ)
    print("Running with seed 101...")
    res3 = engine.generate_daily_activity(world_state, posts, tick_seed=101)
    
    if json.dumps(res1, sort_keys=True) == json.dumps(res2, sort_keys=True):
        print("✅ SUCCESS: Same tick_seed produced identical output.")
    else:
        print("❌ FAILURE: Output differed for same seed!")
        
    if json.dumps(res1, sort_keys=True) != json.dumps(res3, sort_keys=True):
         print("✅ SUCCESS: Different tick_seed produced different output.")
    else:
         print("⚠️ WARNING: Different seed produced same output (statistically possible but unlikely if N=100)")
         
    # Verify Type field
    if res1 and "type" in res1[0] and res1[0]["type"] == "comment":
        print("✅ SUCCESS: Output contains 'type': 'comment'")
    else:
        print("❌ FAILURE: Missing 'type' field.")

if __name__ == "__main__":
    test_tick_determinism()
