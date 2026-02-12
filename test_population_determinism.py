"""
Deterministic Unit Test for PopulationEngine

Verifies that the engine produces identical output for the same input state.
Now includes faction tension and author_faction data.
"""
from simulation.population_engine import PopulationEngine, UserProfile
import json

def test_daily_determinism():
    print("--- Starting Deterministic Test ---")
    
    # 1. Initialize Engine
    engine = PopulationEngine(size=1000, seed=42)
    
    # 2. Setup World State with Faction Tension
    world_state = {
        "date": "2026-02-11",
        "public_unrest": 0.5,
        "faction_tension": {
            ("bio", "augmented"): 0.9, # High tension
            ("purist", "synthetic"): 0.8
        }
    }
    
    # 3. Setup Mock Posts with Author Faction
    posts = [
        {"id": "post_1", "topic": "economy", "author_faction": "bio"},
        {"id": "post_2", "topic": "tech", "author_faction": "augmented"},
        {"id": "post_3", "topic": "politics", "author_faction": "purist"}
    ]
    
    # 4. Generate Activity (Run 1)
    print("Generating Run 1...")
    result1 = engine.generate_daily_activity(world_state, posts)
    
    # 5. Generate Activity (Run 2 - Same State)
    print("Generating Run 2...")
    result2 = engine.generate_daily_activity(world_state, posts)
    
    # 6. Compare Results
    # We compare the JSON representation to ensure deep equality including all fields
    json1 = json.dumps(result1, sort_keys=True)
    json2 = json.dumps(result2, sort_keys=True)
    
    if json1 == json2:
        print(f"✅ SUCCESS: Results are identical.")
        print(f"Run 1 Count: {len(result1)}")
        print(f"Run 2 Count: {len(result2)}")
        
        # Verify aggressive comments exist (indicating tension worked)
        aggressive_count = sum(1 for c in result1 if c['content'] in engine.COMMENTS_AGGRESSIVE)
        print(f"Aggressive Comments: {aggressive_count}")
        
    else:
        print(f"❌ FAILURE: Results differ!")
        print(f"Run 1 Count: {len(result1)}")
        print(f"Run 2 Count: {len(result2)}")
        exit(1)

if __name__ == "__main__":
    test_daily_determinism()
