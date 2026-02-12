"""
Test TickContext class.
"""

from core.tick_context import TickContext


def test_tick_context():
    """Test TickContext creation and behavior."""
    print("=== Testing TickContext ===\n")
    
    base_seed = 42
    
    # Create context for tick 1
    ctx1 = TickContext(base_seed=base_seed, tick_number=1, mode="simulation")
    
    print(f"Tick 1:")
    print(f"  tick_number: {ctx1.tick_number}")
    print(f"  tick_seed: {ctx1.tick_seed}")
    print(f"  timestamp: {ctx1.timestamp}")
    print(f"  mode: {ctx1.mode}")
    
    # Verify tick_seed calculation
    expected_seed_1 = base_seed + 1
    assert ctx1.tick_seed == expected_seed_1, f"Expected {expected_seed_1}, got {ctx1.tick_seed}"
    print(f"✅ tick_seed correctly computed: {base_seed} + 1 = {ctx1.tick_seed}\n")
    
    # Create context for tick 100
    ctx100 = TickContext(base_seed=base_seed, tick_number=100, mode="hybrid")
    
    print(f"Tick 100:")
    print(f"  tick_number: {ctx100.tick_number}")
    print(f"  tick_seed: {ctx100.tick_seed}")
    print(f"  mode: {ctx100.mode}")
    
    expected_seed_100 = base_seed + 100
    assert ctx100.tick_seed == expected_seed_100, f"Expected {expected_seed_100}, got {ctx100.tick_seed}"
    print(f"✅ tick_seed correctly computed: {base_seed} + 100 = {ctx100.tick_seed}\n")
    
    # Test to_dict()
    print("Testing to_dict():")
    ctx_dict = ctx1.to_dict()
    print(f"  {ctx_dict}")
    
    assert "tick_number" in ctx_dict
    assert "tick_seed" in ctx_dict
    assert "timestamp" in ctx_dict
    assert "mode" in ctx_dict
    print("✅ to_dict() includes all required fields\n")
    
    # Verify determinism (same inputs -> same tick_seed)
    ctx1_copy = TickContext(base_seed=base_seed, tick_number=1, mode="simulation")
    assert ctx1.tick_seed == ctx1_copy.tick_seed
    print("✅ Deterministic: same inputs produce same tick_seed\n")
    
    print("=== All Tests Passed ===")


if __name__ == "__main__":
    test_tick_context()
