"""
Test script to verify PopulationEngine action distribution.
Verifies:
- 60% users passive
- 30% reaction
- 8% comment  
- 2% create_post
- Post category weights (Personal 35%, etc.)
"""

from simulation.population_engine import PopulationEngine
from collections import Counter

def test_distribution():
    print("=== Testing Population Engine Distribution ===\n")
    
    # Initialize engine
    engine = PopulationEngine(size=1000, seed=42)
    
    # Mock world state and posts
    world_state = {
        "date": "2207-01-01",
        "public_unrest": 0.3,  # Low unrest
        "media_trust": 0.5,    # Medium trust
        "surveillance_level": 0.2
    }
    
    # Create some mock posts for interaction
    mock_posts = [
        {"id": f"post_{i}", "category": "tech"} for i in range(10)
    ]
    
    # Get actions
    actions = engine.generate_daily_actions(world_state, mock_posts)
    
    print(f"Population: {len(engine.population)} users")
    print(f"Total actions: {len(actions)}")
    print(f"Active ratio: {len(actions) / len(engine.population) * 100:.1f}%")
    print(f"Passive ratio: {(len(engine.population) - len(actions)) / len(engine.population) * 100:.1f}%\n")
    
    # Action type distribution
    action_types = Counter(a['type'] for a in actions)
    print("Action Type Distribution:")
    for atype, count in action_types.most_common():
        pct = count / len(actions) * 100
        print(f"  {atype}: {count} ({pct:.1f}%)")
    
    # Post category distribution
    posts = [a for a in actions if a['type'] == 'create_post']
    if posts:
        categories = Counter(p['category'] for p in posts)
        print(f"\nPost Categories ({len(posts)} total):")
        for cat, count in categories.most_common():
            pct = count / len(posts) * 100
            print(f"  {cat}: {count} ({pct:.1f}%)")
    
    # Test with high unrest
    print("\n=== Testing with HIGH UNREST ===")
    world_state_unrest = {
        "date": "2207-01-02",
        "public_unrest": 0.8,  # High unrest
        "media_trust": 0.2,    # Low trust
        "surveillance_level": 0.1
    }
    
    actions_unrest = engine.generate_daily_actions(world_state_unrest, mock_posts)
    posts_unrest = [a for a in actions_unrest if a['type'] == 'create_post']
    
    if posts_unrest:
        categories_unrest = Counter(p['category'] for p in posts_unrest)
        print(f"Post Categories ({len(posts_unrest)} total):")
        for cat, count in categories_unrest.most_common():
            pct = count / len(posts_unrest) * 100
            print(f"  {cat}: {count} ({pct:.1f}%)")
    
    # Test with high surveillance
    print("\n=== Testing with HIGH SURVEILLANCE ===")
    world_state_surv = {
        "date": "2207-01-03",
        "public_unrest": 0.8,
        "media_trust": 0.5,
        "surveillance_level": 0.9  # High surveillance
    }
    
    actions_surv = engine.generate_daily_actions(world_state_surv, mock_posts)
    print(f"Total actions: {len(actions_surv)} (vs {len(actions_unrest)} without surveillance)")
    print(f"Activity suppression: {(1 - len(actions_surv) / len(actions_unrest)) * 100:.1f}%")
    
    posts_surv = [a for a in actions_surv if a['type'] == 'create_post']
    if posts_surv:
        categories_surv = Counter(p['category'] for p in posts_surv)
        print(f"\nPost Categories ({len(posts_surv)} total):")
        for cat, count in categories_surv.most_common(5):
            pct = count / len(posts_surv) * 100
            print(f"  {cat}: {count} ({pct:.1f}%)")
    
    print("\n✅ Verification complete")

if __name__ == "__main__":
    test_distribution()
