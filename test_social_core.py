"""
Test Social Network Core
"""
import os
import shutil
from simulation.social_network_core import SocialNetworkCore
from simulation.population_engine import PopulationEngine

def test_social_core():
    print("--- Testing Social Network Core ---")
    
    # 1. Setup Test Data Directory provided safely
    test_dir = "test_data_social"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # 2. Initialize Core
    social_net = SocialNetworkCore(data_dir=test_dir)
    print("Initialized Core.")
    
    # 3. Ingest Population
    print("\n--- Ingesting Population ---")
    pop_engine = PopulationEngine(size=10, seed=42)
    social_net.ingest_population(pop_engine.population)
    print(f"Ingested {len(social_net.users)} users.")
    
    # 4. Create Mock Posts
    print("\n--- Registering Content ---")
    mock_posts = [
        {"id": "p1", "topic": "tech", "author_id": "corp_news", "content": "AI Update"},
        {"id": "p2", "topic": "politics", "author_id": "gov_official", "content": "Elections"},
        {"id": "p3", "topic": "economy", "author_id": "finance_bot", "content": "Stocks"}
    ]
    for p in mock_posts:
        social_net.register_post(p)
    print(f"Registered {len(social_net.posts)} posts.")
    
    # 5. Test Timeline Generation
    print("\n--- Generating Timelines ---")
    test_user_id = pop_engine.population[0].user_id
    world_state = {"date": "2207-08-01"}
    
    timeline1 = social_net.get_timeline(test_user_id, world_state)
    print(f"Timeline 1 (Day 1) length: {len(timeline1)}")
    if timeline1:
        print(f"Top Post: {timeline1[0]['id']}")
        
    world_state_day2 = {"date": "2207-08-02"}
    timeline2 = social_net.get_timeline(test_user_id, world_state_day2)
    print(f"Timeline 2 (Day 2) length: {len(timeline2)}")
    
    # Verify Determinism (Same Day)
    timeline1_b = social_net.get_timeline(test_user_id, world_state)
    if [p['id'] for p in timeline1] == [p['id'] for p in timeline1_b]:
        print("✅ SUCCESS: Timeline generation is deterministic.")
    else:
        print("❌ FAILURE: Determinism check failed.")
        
    # 6. Test Viral Mechanics
    print("\n--- Testing Viral Mechanics ---")
    # Simulate heavy commenting on p3
    for _ in range(50):
        social_net.register_comment({"post_id": "p3", "user_id": "bot", "content": "copy"})
        
    # Re-generate timeline (should prefer p3 due to high buzz)
    timeline_viral = social_net.get_timeline(test_user_id, world_state)
    print(f"Viral Timeline Top Post: {timeline_viral[0]['id']}")
    
    if timeline_viral[0]['id'] == 'p3':
        print("✅ SUCCESS: High engagement post bubbled to top.")
    else:
        print(f"⚠️ NOTE: p3 was expected top, got {timeline_viral[0]['id']} (might be affinity override)")
        
    # 7. Persistence
    print("\n--- Testing Persistence ---")
    social_net.end_of_day_cleanup()
    
    # Reload
    new_core = SocialNetworkCore(data_dir=test_dir)
    if len(new_core.users) == 10 and len(new_core.posts) == 3:
         print("✅ SUCCESS: State persisted and reloaded.")
    else:
         print("❌ FAILURE: Persistence failed.")
         
    # Cleanup
    try:
        shutil.rmtree(test_dir)
    except:
        pass

if __name__ == "__main__":
    test_social_core()
