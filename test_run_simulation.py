
from simulation.scheduler import DailyScheduler
import os
import shutil

def test_run():
    print("--- Testing DailyScheduler with UniverseRuntime ---")
    
    # Use a temp dir for data to avoid messing up real simulation data
    test_dir = "data_test_scheduler"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    scheduler = DailyScheduler(data_dir=test_dir)
    scheduler.initialize()
    
    print("Running for 2 days...")
    scheduler.run_for_days(2)
    
    state = scheduler.get_current_state()
    print("Final State Summary:")
    print(state)
    
    # Check if social network data exists
    users_path = os.path.join(test_dir, "social_users.json")
    content_path = os.path.join(test_dir, "social_content.json")
    
    if os.path.exists(users_path):
        print("✅ Social Users file created.")
    else:
        print("❌ Social Users file MISSING.")
        
    if os.path.exists(content_path):
        print("✅ Social Content file created.")
    else:
        print("❌ Social Content file MISSING.")

    print("--- Test Complete ---")

if __name__ == "__main__":
    test_run()
