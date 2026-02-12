"""
Test Emergent Behavior logic
"""
import math
from simulation.population_engine import PopulationEngine
from content.social_impact import SocialImpactProcessor
from core.universe_runtime import UniverseRuntime
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
    world = {"public_unrest": 0.0, "date": "2207-01-01"}
    
    # Measure response rate to tech vs politics (simplistic check)
    # Since it's probabilistic, we run N times
    tech_hits = 0
    poli_hits = 0
    N = 200
    
    for i in range(N):
        res = engine.generate_daily_activity(world, posts_tech, tick_seed=i)
        if any(c['user_id'] == user.user_id for c in res):
            tech_hits += 1
            
        res = engine.generate_daily_activity(world, posts_poli, tick_seed=i)
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
    
    # Mock world state wrapper
    class MockState:
        def __init__(self):
            self.effects = []
            self.public_unrest = 0.5
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
    
    # Create runtime with partial mocks
    ws = WorldState({"public_unrest": 0.8}) # High unrest to trigger echo
    runtime = UniverseRuntime(ws, engine, processor, None, None, None, None, tick_interval_seconds=0)
    
    # Tick 1: Should schedule echo
    runtime.run_tick() 
    print(f"Tick 1: Delayed Events: {len(runtime.delayed_events)}")
    
    if len(runtime.delayed_events) == 1 and runtime.delayed_events[0]["type"] == "echo_unrest":
        print("✅ SUCCESS: Echo event scheduled.")
    else:
        print("❌ FAILURE: Echo scheduling failed.")
        
    # Tick 2, 3: Wait
    runtime.run_tick()
    runtime.run_tick()
    
    # Tick 4: Execute (Ticket #1 + 3 = 4)
    # Capture apply_effect call via mock or just check state
    # Since WorldState is real, we check last_effects
    runtime.run_tick()
    
    found_echo = any(e['source'] == 'delayed_echo' for e in ws.last_effects)
    if found_echo:
        print("✅ SUCCESS: Echo event executed impact.")
    else:
        print("❌ FAILURE: Echo execution not found in history.")

if __name__ == "__main__":
    test_emergent_features()
