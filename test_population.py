"""
Test Population Engine (Deterministic)
"""
from simulation.population_engine import PopulationEngine, UserProfile
import json
import copy

# Initialize
print("--- Initializing Population ---")
pop_engine = PopulationEngine(size=1000, seed=123)

# Mock world state and posts
world_state_day1 = {
    "public_unrest": 0.5,
    "media_trust": 0.5,
    "surveillance_level": 0.5,
    "date": "2207-06-01"  # Crucial for deterministic seed
}
posts = [{"id": "post_1", "content": "News"}]

# Test 1: Run twice with same state, should be IDENTICAL
print("\n--- Testing Determinism (Same Day) ---")
run1 = pop_engine.generate_daily_activity(world_state_day1, posts)
run2 = pop_engine.generate_daily_activity(world_state_day1, posts)

print(f"Run 1 generated {len(run1)} comments.")
print(f"Run 2 generated {len(run2)} comments.")

ids1 = [c['user_id'] + c['content'] for c in run1]
ids2 = [c['user_id'] + c['content'] for c in run2]

if ids1 == ids2:
    print("✅ SUCCESS: Output is identical for same day/state.")
else:
    print("❌ FAILURE: Output differs for same day/state!")
    print(f"Difference: {set(ids1) ^ set(ids2)}")

# Test 2: Different day, should be DIFFERENT
print("\n--- Testing Variance (Different Day) ---")
world_state_day2 = copy.deepcopy(world_state_day1)
world_state_day2["date"] = "2207-06-02"

run3 = pop_engine.generate_daily_activity(world_state_day2, posts)
print(f"Run 3 (Day 2) generated {len(run3)} comments.")

ids3 = [c['user_id'] + c['content'] for c in run3]
if ids1 != ids3:
    print("✅ SUCCESS: Output differs for different day.")
else:
    print("❌ FAILURE: Output is identical for different days (stagnant RNG).")
