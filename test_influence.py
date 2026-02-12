"""
Test internal Influence Engine logic
"""
from simulation.influence_engine import InfluenceEngine

def test_influence_engine():
    print("--- Testing Influence Engine ---")
    
    engine = InfluenceEngine()
    
    # 1. Setup Entity
    entity = {
        "id": "user1",
        "influence_score": 10.0,
        "reputation_score": 0.0,
        "chaos_affinity": 0.0,
        "trust_alignment": 0.5
    }
    
    # 2. Test Calculate Deltas
    # Case A: High Engagement, No AI replies
    print("\n[1] Testing Engagement Only...")
    engagement_a = {"comments": 10, "replies": 5} # 15 interactions
    deltas_a = engine.calculate_influence_delta(entity, engagement_a, {"public_unrest": 0.2})
    # Should yield positive influence delta
    gain = deltas_a.get("influence_score", 0)
    print(f"Influence Gain (15 interactions): {gain:.3f}")
    
    if gain > 0:
        print("✅ SUCCESS: Influence gained from engagement.")
    else:
        print("❌ FAILURE: No influence gain detected.")

    # Apply & Check
    engine.apply_influence(entity, deltas_a)
    print(f"New Influence: {entity['influence_score']:.3f} (Was 10.0)")
    
    if entity["influence_score"] > 10.0:
        print("✅ SUCCESS: Delta applied correctly.")
    else:
        print("❌ FAILURE: Apply logic failed.")
        
    # 3. Test World Metric Interaction
    # Case B: High Unrest, Moderate Engagement -> Chaos Up
    print("\n[2] Testing World Metrics (Unrest)...")
    engagement_b = {"comments": 6}
    world_b = {"public_unrest": 0.8, "media_trust": 0.5}
    deltas_b = engine.calculate_influence_delta(entity, engagement_b, world_b)
    
    chaos_delta = deltas_b.get("chaos_affinity", 0)
    print(f"Chaos Delta (Unrest 0.8): {chaos_delta:.4f}")
    
    if chaos_delta > 0:
        print("✅ SUCCESS: Chaos affinity increased due to high unrest.")
    else:
        print("❌ FAILURE: Chaos logic failed.")
        
    # 4. Test Decay (Run multiple ticks to verify decay)
    print("\n[3] Testing Decay...")
    start_inf = entity["influence_score"]
    decay_count = 10
    
    for _ in range(decay_count):
        engine.decay_influence(entity, rate=0.05)
    
    print(f"Start: {start_inf:.3f} -> End ({decay_count} ticks): {entity['influence_score']:.3f}")
    
    if entity["influence_score"] < start_inf:
        print("✅ SUCCESS: Influence decayed over time.")
    else:
        print("❌ FAILURE: Decay logic failed.")
        
    # 5. Clamp Check
    print("\n[4] Testing Clamping...")
    entity["influence_score"] = 99.9
    # Add huge delta
    deltas_c = {"influence_score": 50.0}
    engine.apply_influence(entity, deltas_c)
    
    print(f"Clamped Influence: {entity['influence_score']}")
    
    if entity['influence_score'] == 100.0:
        print("✅ SUCCESS: Max influence clamped correctly.")
    else:
         print(f"❌ FAILURE: Influence exceeded max ({entity['influence_score']})")


if __name__ == "__main__":
    test_influence_engine()
