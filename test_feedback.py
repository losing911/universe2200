"""
Test script to demonstrate feedback loops and effect traceability
in the 2200 Evreni simulation engine.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from simulation.scheduler import DailyScheduler


def main():
    """Run a short simulation and display effect tracking."""
    print("=" * 70)
    print("   2200 Evreni - Feedback Loop Demonstration")
    print("=" * 70)
    print()
    
    # Reset world state to high-activity scenario
    from core.world import WorldManager
    world = WorldManager()
    world.load_world()
    
    # Set high initial values to trigger events
    world.state.water_price_index = 1.7
    world.state.public_unrest = 0.55
    world.state.media_trust = 0.35
    world.save_world()
    
    print("🔧 Reset world state to high-activity scenario:")
    print(f"   Water Price: {world.state.water_price_index}")
    print(f"   Public Unrest: {world.state.public_unrest}")
    print(f"   Media Trust: {world.state.media_trust}")
    print()
    
    # Create scheduler and run simulation for just 10 days
    scheduler = DailyScheduler()
    scheduler.initialize()
    
    print("⚙️  Running 10-day simulation...\n")
    
    for day in range(10):
        summary = scheduler.run_daily_tick()
        
        if summary['events_generated']:
            print(f"📅 Day {day + 1}: {summary['date']}")
            print(f"   Events: {len(summary['events_generated'])}")
            
            for event in summary['events_generated']:
                print(f"   • {event.type.upper()}: {event.description[:50]}...")
                
                # Show feedback effects
                if 'effects_applied' in event.metadata:
                    print("     💫 Event Effects Applied:")
                    for metric, delta in event.metadata['effects_applied'].items():
                        sign = "+" if delta > 0 else ""
                        print(f"        {metric}: {sign}{delta}")
                
                # Show trigger conditions
                if 'triggered_by_state' in event.metadata:
                    print(f"     🎯 Triggered by: {', '.join(event.metadata['triggered_by_state'])}")
            
            print()
    
    # Show effect history
    print("\n" + "=" * 70)
    print("   Effect History (Last 10 effects)")
    print("=" * 70)
    
    effect_history = scheduler.engine.world.state.last_effects[-10:]
    
    if effect_history:
        for i, effect in enumerate(effect_history, 1):
            print(f"\n{i}. Source: {effect['source']}")
            print(f"   Date: {effect['date']}")
            print(f"   Effects:")
            for metric, delta in effect['effects'].items():
                sign = "+" if delta > 0 else ""
                print(f"      • {metric}: {sign}{delta:.3f}")
    else:
        print("\nNo effects recorded yet.")
    
    print("\n" + "=" * 70)
    print("✅ Feedback loop demonstration complete!")
    print(f"📊 Total effects tracked: {len(scheduler.engine.world.state.last_effects)}")
    print()


if __name__ == "__main__":
    main()
