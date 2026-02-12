"""
Test ContentPipeline module.
"""

import json
from core.content_pipeline import ContentPipeline
from core.tick_context import TickContext
from core.state import WorldState


def test_content_pipeline():
    """Test ContentPipeline with various scenarios."""
    print("=== Testing ContentPipeline ===\n")
    
    pipeline = ContentPipeline()
    
    # Scenario 1: High unrest
    print("Scenario 1: High Unrest State")
    print("-" * 50)
    
    world_state_high_unrest = WorldState({
        'public_unrest': 0.95,
        'media_trust': 0.15,
        'information_noise': 0.85,
        'surveillance_level': 0.70,
        'ai_dependency': 0.60,
        'corp_power_index': 0.75
    })
    
    tick_ctx = TickContext(base_seed=42, tick_number=1, mode="simulation")
    
    output = pipeline.run(tick_ctx, world_state_high_unrest)
    
    print(f"Headline: {output['headline']}")
    print(f"Events Detected: {output['events_detected']}")
    print(f"News Articles: {len(output['news'])}")
    print(f"Social Posts: {len(output['social_feed'])}")
    print(f"Trending Topics: {len(output['trending'])}")
    print()
    
    # Print first news article
    if output['news']:
        print("Sample News Article:")
        print(f"  Title: {output['news'][0]['title']}")
        print(f"  Summary: {output['news'][0]['summary']}")
        print()
    
    # Print trending topics
    print("Trending Topics:")
    for topic in output['trending']:
        print(f"  {topic['tag']} ({topic['volume']})")
    print()
    
    # Scenario 2: Stable state
    print("\nScenario 2: Stable State")
    print("-" * 50)
    
    world_state_stable = WorldState({
        'public_unrest': 0.30,
        'media_trust': 0.65,
        'information_noise': 0.20,
        'surveillance_level': 0.40
    })
    
    tick_ctx_2 = TickContext(base_seed=42, tick_number=2, mode="simulation")
    output_stable = pipeline.run(tick_ctx_2, world_state_stable)
    
    print(f"Headline: {output_stable['headline']}")
    print(f"Events Detected: {output_stable['events_detected']}")
    print(f"News Articles: {len(output_stable['news'])}")
    print()
    
    # Scenario 3: Systemic crisis
    print("\nScenario 3: Systemic Crisis")
    print("-" * 50)
    
    world_state_crisis = WorldState({
        'public_unrest': 1.0,
        'media_trust': 0.0,
        'information_noise': 1.0,
        'surveillance_level': 0.9,
        'corp_power_index': 0.85
    })
    
    tick_ctx_3 = TickContext(base_seed=42, tick_number=3, mode="simulation")
    output_crisis = pipeline.run(tick_ctx_3, world_state_crisis)
    
    print(f"Headline: {output_crisis['headline']}")
    print(f"Events Detected: {output_crisis['events_detected']}")
    print(f"Severity: Critical events = {len([e for e in output_crisis['events_detected'] if 'critical' in e.lower()])}")
    print()
    
    # Test JSON serialization
    print("\n=== Testing JSON Output ===")
    print("-" * 50)
    
    json_output = json.dumps(output, indent=2)
    print("JSON output successfully serialized")
    print(f"Output size: {len(json_output)} bytes")
    
    # Verify structure
    required_keys = ["tick", "headline", "news", "social_feed", "trending", "metrics"]
    missing_keys = [k for k in required_keys if k not in output]
    
    if missing_keys:
        print(f"❌ Missing keys: {missing_keys}")
    else:
        print("✅ All required keys present")
    
    # Test determinism
    print("\n=== Testing Determinism ===")
    print("-" * 50)
    
    output_repeat = pipeline.run(tick_ctx, world_state_high_unrest)
    
    if output['headline'] == output_repeat['headline']:
        print("✅ Headlines match (deterministic)")
    else:
        print("❌ Headlines differ (non-deterministic)")
    
    if len(output['news']) == len(output_repeat['news']):
        print("✅ News count matches (deterministic)")
    else:
        print("❌ News count differs (non-deterministic)")
    
    print("\n=== All Tests Complete ===")


if __name__ == "__main__":
    test_content_pipeline()
