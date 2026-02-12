"""
Test Event Scheduler logic
"""
from simulation.event_scheduler import EventScheduler

class MockWorldState:
    def __init__(self):
        self.metrics = {"public_unrest": 0.5, "media_trust": 0.5}
        self.applied_effects = []

    def apply_effect(self, source, effects):
        self.applied_effects.append({"source": source, "effects": effects})
        for k, v in effects.items():
            if k in self.metrics:
                self.metrics[k] += v

def test_event_scheduler():
    print("--- Testing Event Scheduler ---")
    
    scheduler = EventScheduler(seed=42)
    world = MockWorldState()
    
    # 1. Scheduling an Event
    print("\n[1] Testing Scheduled Event...")
    scheduler.schedule_event(5, "AI Uprising")
    
    # Tick 1-4: Nothing
    for t in range(1, 5):
        scheduler.check_for_events(t)
        scheduler.apply_event_effects(world)
        if scheduler.active_events:
            print(f"❌ FAILURE: Event started too early at tick {t}")
            return

    # Tick 5: Trigger
    print("Advancing to Tick 5...")
    triggered = scheduler.check_for_events(5)
    scheduler.apply_event_effects(world)
    
    if triggered and triggered[0]["name"] == "AI Uprising":
         print("✅ SUCCESS: 'AI Uprising' triggered on schedule.")
    else:
         print("❌ FAILURE: Scheduled event did not trigger.")

    # Check Effects on World
    # AI Uprising effect: unrest +0.15
    # World metrics should change
    # Note: apply_event_effects calls apply_effect
    if any(e["source"] == "Event: AI Uprising" for e in world.applied_effects):
        print("✅ SUCCESS: World effect applied.")
    else:
        print("❌ FAILURE: No world effect found.")

    # Check Modifiers
    mods = scheduler.get_active_modifiers()
    # AI Uprising: influence_mod 1.2
    if mods["influence_mult"] == 1.2:
        print("✅ SUCCESS: Influence modifier active (1.2x).")
    else:
        print(f"❌ FAILURE: Incorrect modifier: {mods.get('influence_mult')}")

    # 2. Duration & Expiry
    print("\n[2] Testing Duration & Expiry...")
    # AI Uprising duration is 5. We just did tick 5 (duration became 4).
    # Need 4 more ticks to expire?
    # duration counts down in apply_event_effects
    
    initial_applied_count = len(world.applied_effects)
    
    for _ in range(4): # Tick 6, 7, 8, 9
        scheduler.check_for_events(10) # Tick doesn't matter for duration, just calls apply
        scheduler.apply_event_effects(world)
        
    if not scheduler.active_events:
        print("✅ SUCCESS: Event expired correctly.")
    else:
        print(f"❌ FAILURE: Event still active: {scheduler.active_events}")

    # 3. Random Events
    print("\n[3] Testing Random Events (Deterministic)...")
    # Scheduler seed 42. Tick 20 is random check.
    # We reset scheduler or just use current state?
    # New scheduler for clean determinism test
    sched2 = EventScheduler(seed=42)
    
    # Tick 20
    triggered = sched2.check_for_events(20)
    if triggered:
        print(f"Tick 20 Triggered: {[e['name'] for e in triggered]}")
    else:
        print("Tick 20: No random event.")
        
    # Python random(42) -> first float is 0.639... > 0.3 (threshold) -> No event?
    # Let's find a seed/tick that triggers.
    # Or just loop.
    
    found_event = False
    for t in range(20, 201, 20):
        trig = sched2.check_for_events(t)
        if trig:
            print(f"Found event at tick {t}: {trig[0]['name']}")
            found_event = True
            break
            
    if found_event:
        print("✅ SUCCESS: Random event triggered.")
    else:
        print("⚠️ WARNING: No random event in 200 ticks (bad luck or logic?)")

if __name__ == "__main__":
    test_event_scheduler()
