"""
2200 Evreni - Simulation-Driven Living Universe

Main entry point for the universe simulation engine.
"""

import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from simulation.scheduler import DailyScheduler


def main():
    """Run the simulation."""
    print("=" * 70)
    print("   2200 Evreni - Living Universe Simulation Engine")
    print("=" * 70)
    print()
    
    # Create scheduler
    scheduler = DailyScheduler()
    
    # Initialize the simulation
    scheduler.initialize()
    
    # Run simulation for 30 days (configurable)
    num_days = 30
    scheduler.run_for_days(num_days)
    
    # Print final summary
    final_state = scheduler.get_current_state()
    print()
    print("=" * 70)
    print("   Final State Summary")
    print("=" * 70)
    print(f"📅 Final Date: {final_state['date']}")
    print(f"📊 Total Events in Log: {final_state['num_events']}")
    print()
    print("Metrics:")
    for metric, value in final_state['metrics'].items():
        print(f"   • {metric}: {value:.3f}")
    print()
    print("✅ Data saved to data/ directory")
    print()


if __name__ == "__main__":
    main()
