"""
Test Emergent Behavior logic
"""
import unittest
from unittest.mock import MagicMock
from simulation.population_engine import PopulationEngine
from content.social_impact import SocialImpactProcessor
from core.universe_runtime import UniverseRuntime
from core.config import RuntimeConfig
from core.state import WorldState

def test_emergent_features():
    print("--- Testing Emergent Behavior ---")
    
    # 1. Test Topic Weighted Behavior
    print("\n[1] Testing Topic Weights...")
    engine = PopulationEngine(size=50, seed=42)
    # Set user 0 to love 'tech'
    user = engine.population[0]
    user.topic_affinity = {"tech": 1.0, "politics": 0.0}
    user.activity_level = 0.5
    
    # Mock posts
    posts_tech = [{"id": "p1", "topic": "tech"}]
    posts_poli = [{"id": "p2", "topic": "politics"}]
    world_metrics = {"public_unrest": 0.0, "date": "2207-01-01"} # PopulationEngine uses dict for metrics, not WorldState object
    
    # Measure response rate to tech vs politics (simplistic check)
    # Since it's probabilistic, we run N times
    tech_hits = 0
    poli_hits = 0
    N = 200
    
    for i in range(N):
        res = engine.generate_daily_activity(world_metrics, posts_tech, tick_seed=i)
        if any(c['user_id'] == user.user_id for c in res):
            tech_hits += 1
            
        res = engine.generate_daily_activity(world_metrics, posts_poli, tick_seed=i)
        if any(c['user_id'] == user.user_id for c in res):
            poli_hits += 1
            
    print(f"Tech Hits: {tech_hits}, Poli Hits: {poli_hits}")
    if tech_hits > poli_hits:
        print("✅ SUCCESS: User preferred affinity topic.")
    else:
        print("❌ FAILURE: Preference logic weak or broken.")

    # 2. Test Viral Multiplier in SocialImpact
    print("\n[2] Testing Viral Multiplier...")
    processor = SocialImpactProcessor()
    
    # Mock world state wrapper for SocialImpact
    class MockState:
        def __init__(self):
            self.effects = []
            self.public_unrest = 0.5
            self.media_trust = 0.5
            self.surveillance_level = 0.5
            self.information_noise = 0.5
        def apply_effect(self, src, eff):
            self.effects.append(eff)
        def get_metric(self, m): return getattr(self, m, 0.5)

    # Case A: 1 comment
    state_a = MockState()
    comments_a = [{"content": "riot"}] # Unrest keyword
    processor.apply_impact({"id": "p1"}, comments_a, None, state_a)
    effect_a = state_a.effects[0]["public_unrest"]
    
    # Case B: 100 comments
    state_b = MockState()
    comments_b = [{"content": "riot"} for _ in range(100)]
    processor.apply_impact({"id": "p2"}, comments_b, None, state_b)
    effect_b = state_b.effects[0]["public_unrest"]
    
    print(f"Effect (1 comment): {effect_a:.5f}")
    print(f"Effect (100 comments): {effect_b:.5f}")
    
    # Logic: 1 comment -> log10(2)+1 ~ 1.3x
    # 100 comments -> log10(101)+1 ~ 3.0x
    # Total impact = sum(signals) * viral_factor
    # signal_a = 1 * sentiment_weight * 1.3
    # signal_b = 100 * sentiment_weight * 3.0
    # ratio should be massive
    
    # Re-evaluate Test:
    # Effect B should be much larger OR hit max clamp (0.05).
    # Effect A is ~0.0065
    # If Effect B is 0.05, that's already ~7.6x, so the viral multiplier pushed it to max.
    
    if effect_b >= 0.045: # Close to max clamp
        print("✅ SUCCESS: Viral multiplier pushed impact to clamp limit.")
    elif effect_b > effect_a * 2.0:
        print("✅ SUCCESS: Viral multiplier verified (sub-clamp).")
    else:
        print("❌ FAILURE: Viral multiplier logic suspect.")
        
    # 3. Test Delayed Echo
    print("\n[3] Testing Delayed Echo...")
    
    # Create valid Runtime components
    config = RuntimeConfig(tick_interval_seconds=0, mode="simulation")
    ws = WorldState({"public_unrest": 0.8}) # High unrest to trigger echo
    
    # Mock pipelines
    mock_activity_pipeline = MagicMock()
    mock_activity_pipeline.run.return_value = [] # Return empty affected posts
    
    mock_reply_pipeline = MagicMock()
    mock_impact_pipeline = MagicMock()
    
    runtime = UniverseRuntime(
        config=config,
        world_state=ws,
        activity_pipeline=mock_activity_pipeline,
        reply_pipeline=mock_reply_pipeline,
        impact_pipeline=mock_impact_pipeline
    )
    
    # Manually schedule a delayed event (normally done by some logic, here we inject it)
    runtime.delayed_events.append({
        "type": "echo_unrest",
        "execute_at": 2 # Execute on tick 2
    })
    
    # Tick 1: Should NOT execute yet
    print("Running Tick 1...")
    runtime.run_tick() 
    
    found_echo_t1 = any(entry['source'] == 'delayed_echo' for entry in ws.last_effects)
    if not found_echo_t1:
        print("✅ SUCCESS: Echo event waited (Tick 1).")
    else:
        print("❌ FAILURE: Echo executed too early.")
    
    # Tick 2: Should execute
    print("Running Tick 2...")
    runtime.run_tick()
    
    found_echo_t2 = any(entry['source'] == 'delayed_echo' for entry in ws.last_effects)
    
    # Debug info
    # print(f"Last effects: {ws.last_effects}")
    
    if found_echo_t2:
        print("✅ SUCCESS: Echo event executed impact (Tick 2).")
    else:
        print("❌ FAILURE: Echo execution not found in history.")

if __name__ == "__main__":
    test_emergent_features()
