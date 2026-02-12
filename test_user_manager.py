"""
Test User Manager logic
"""
from core.user_manager import UserManager, UserEntity
from simulation.influence_engine import InfluenceEngine

def test_user_system():
    print("--- Testing User Management System ---")
    
    # 1. Setup Manager with Real Influence Engine
    inf_engine = InfluenceEngine()
    manager = UserManager(influence_engine=inf_engine)
    
    # 2. Register User
    print("\n[1] Registering User 'Neo'...")
    user = manager.register_user("Neo", faction="activist")
    
    if user and user.username == "Neo":
        print(f"✅ SUCCESS: User registered with ID: {user.user_id}")
    else:
        print("❌ FAILURE: User registration failed.")
        return

    # 3. Authenticate User
    print("\n[2] Authenticating 'Neo'...")
    auth_user = manager.authenticate_user("Neo")
    
    if auth_user and auth_user.last_active:
        print("✅ SUCCESS: User authenticated and activity updated.")
    else:
        print("❌ FAILURE: Authentication failed.")

    # 4. Metric Update via Influence Engine
    print("\n[3] Testing Metric Update...")
    initial_inf = user.influence_score
    print(f"Initial Influence: {initial_inf}")
    
    # Simulate high engagement
    engagement = {"comments": 20, "replies": 5}
    world = {"public_unrest": 0.5, "media_trust": 0.5}
    
    # Update
    deltas = manager.update_user_metrics(user.user_id, engagement, world)
    
    print(f"Deltas Calculated: {deltas}")
    print(f"New Influence: {user.influence_score}")
    
    if user.influence_score > initial_inf:
        print("✅ SUCCESS: Influence metrics updated.")
    else:
        print("❌ FAILURE: Metrics did not change.")

    # 5. Duplicate Registration Check
    print("\n[4] Testing Duplicate Registration...")
    dup = manager.register_user("Neo")
    if dup is None:
        print("✅ SUCCESS: Duplicate registration prevented.")
    else:
        print("❌ FAILURE: Allowed duplicate username.")

if __name__ == "__main__":
    test_user_system()
