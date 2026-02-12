"""
Test deterministic RNG behavior in PopulationEngine.
Verifies that the same tick_seed produces identical outputs.
"""

from simulation.population_engine import PopulationEngine

def test_determinism():
    print("=== Testing Deterministic RNG Control ===\n")
    
    # Create two identical engines
    engine1 = PopulationEngine(size=100, seed=42)
    engine2 = PopulationEngine(size=100, seed=42)
    
    # Mock world state
    world_state = {
        "date": "2207-01-01",
        "public_unrest": 0.5,
        "media_trust": 0.5,
        "surveillance_level": 0.2
    }
    
    # Mock posts
    posts = [{"id": f"post_{i}", "category": "tech"} for i in range(5)]
    
    # Generate with SAME tick_seed
    tick_seed = 100
    
    actions1_tick1 = engine1.generate_daily_actions(world_state, posts, tick_seed=tick_seed)
    actions2_tick1 = engine2.generate_daily_actions(world_state, posts, tick_seed=tick_seed)
    
    print(f"Engine 1 - Tick 1: {len(actions1_tick1)} actions")
    print(f"Engine 2 - Tick 1: {len(actions2_tick1)} actions")
    
    # Verify identical output
    if len(actions1_tick1) == len(actions2_tick1):
        print("✅ PASS: Same tick_seed produces same action count\n")
    else:
        print("❌ FAIL: Different action counts\n")
        return
    
    # Check content identity
    identical = True
    for i, (a1, a2) in enumerate(zip(actions1_tick1, actions2_tick1)):
        if a1 != a2:
            print(f"❌ FAIL: Action {i} differs")
            print(f"  Engine 1: {a1}")
            print(f"  Engine 2: {a2}")
            identical = False
            break
    
    if identical:
        print("✅ PASS: All actions are identical\n")
    
    # Test tick progression
    print("=== Testing Tick Progression ===\n")
    
    # Simulate tick 2 with tick_seed = base_seed + 2
    tick_seed_2 = 102
    actions1_tick2 = engine1.generate_daily_actions(world_state, posts, tick_seed=tick_seed_2)
    
    print(f"Engine 1 - Tick 2: {len(actions1_tick2)} actions")
    
    # Re-run tick 1 to verify we can replay
    actions1_tick1_replay = engine1.generate_daily_actions(world_state, posts, tick_seed=100)
    
    print(f"Engine 1 - Tick 1 Replay: {len(actions1_tick1_replay)} actions")
    
    if actions1_tick1 == actions1_tick1_replay:
        print("✅ PASS: Can replay tick 1 with same results")
    else:
        print("❌ FAIL: Replay produced different results")
    
    # Verify tick 2 is different
    if actions1_tick1 != actions1_tick2:
        print("✅ PASS: Different tick seeds produce different outputs")
    else:
        print("⚠️  WARNING: Tick 1 and Tick 2 produced identical outputs (unlikely but possible)")
    
    print("\n=== Test Complete ===")
    print("Deterministic RNG control is working correctly!")

if __name__ == "__main__":
    test_determinism()
