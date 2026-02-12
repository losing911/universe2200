"""
Test RuntimeConfig validation and defaults.
"""

from core.config import RuntimeConfig


def test_defaults():
    """Test default configuration values."""
    print("=== Testing RuntimeConfig Defaults ===\n")
    
    config = RuntimeConfig()
    
    print(f"mode: {config.mode}")
    print(f"tick_interval_seconds: {config.tick_interval_seconds}")
    print(f"base_seed: {config.base_seed}")
    print(f"enable_ai_replies: {config.enable_ai_replies}")
    print(f"enable_social_impact: {config.enable_social_impact}")
    print(f"enable_real_users: {config.enable_real_users}")
    print(f"max_posts_per_tick: {config.max_posts_per_tick}")
    print(f"max_comments_per_tick: {config.max_comments_per_tick}")
    
    print("\n✅ Default values loaded successfully")
    
    # Validate default config
    try:
        config.validate()
        print("✅ Default config is valid\n")
    except ValueError as e:
        print(f"❌ Validation failed: {e}\n")


def test_validation():
    """Test configuration validation."""
    print("=== Testing Validation ===\n")
    
    # Test invalid mode
    print("Test 1: Invalid mode")
    config_bad_mode = RuntimeConfig(mode="invalid")
    try:
        config_bad_mode.validate()
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✅ Caught expected error: {e}\n")
    
    # Test valid hybrid mode
    print("Test 2: Valid hybrid mode")
    config_hybrid = RuntimeConfig(mode="hybrid", enable_real_users=True)
    try:
        config_hybrid.validate()
        print("✅ Hybrid mode validated successfully\n")
    except ValueError as e:
        print(f"❌ Unexpected error: {e}\n")
    
    # Test invalid tick interval
    print("Test 3: Invalid tick interval")
    config_bad_tick = RuntimeConfig(tick_interval_seconds=0)
    try:
        config_bad_tick.validate()
        print("❌ Should have raised ValueError")
    except ValueError as e:
        print(f"✅ Caught expected error: {e}\n")
    
    print("=== All Tests Complete ===")


if __name__ == "__main__":
    test_defaults()
    test_validation()
