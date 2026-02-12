"""
Test Full Integration
"""
from simulation.population_engine import PopulationEngine
from simulation.influence_engine import InfluenceEngine
from simulation.ai_reaction_engine import AIReactionEngine
from simulation.event_scheduler import EventScheduler
from content.social_impact import SocialImpactProcessor
from content.social_interaction import CommentManager, ReplyManager, SocialReplyGenerator
from core.universe_runtime import UniverseRuntime
from core.state import WorldState
import threading
import time

class MockSocialNetwork:
    def __init__(self):
        self.posts = [{"id": "p1", "topics": ["tech"], "author_faction": "bio"}]
        self.comments = []
        self.new_posts = []
        
    def register_comment(self, comment):
        self.comments.append(comment)
        
    def register_post(self, post):
        self.new_posts.append(post)
        self.posts.append(post)

class MockReplyGenerator:
    def generate_reply(self, post, comments, world_state):
        return {"content": "Ai Reply"}

def test_full_integration():
    print("--- Testing Full Integration ---")
    
    # 1. Setup Components
    world_state = WorldState({"public_unrest": 0.5})
    pop_engine = PopulationEngine(size=20, seed=42)
    inf_engine = InfluenceEngine()
    ai_engine = AIReactionEngine()
    scheduler = EventScheduler(seed=42)
    impact_proc = SocialImpactProcessor()
    
    # Managers (using memory storage)
    def mock_save_c(post_id, user_handle, content): pass
    def mock_get_c(post_id): return [{"content": "Unrest!"}]
    def mock_save_r(post_id, r): pass
    def mock_get_r(post_id): return None
    
    # Hack manager mocks
    comm_mgr = CommentManager(None) 
    comm_mgr.add_comment = mock_save_c
    comm_mgr.get_comments_for_post = mock_get_c
    
    repl_mgr = ReplyManager(None)
    repl_mgr.save_reply = mock_save_r
    repl_mgr.get_reply = mock_get_r
    
    reply_gen = MockReplyGenerator()
    social_net = MockSocialNetwork()
    
    # 2. Instantiate Runtime with ALL engines
    runtime = UniverseRuntime(
        world_state,
        pop_engine,
        impact_proc,
        comm_mgr,
        repl_mgr,
        reply_gen,
        social_network=social_net,
        influence_engine=inf_engine,
        ai_reaction_engine=ai_engine,
        event_scheduler=scheduler,
        tick_interval_seconds=0 # fast mode
    )
    
    # 3. Trigger Manual Event
    print("[1] Scheduling Event for Tick 2...")
    scheduler.schedule_event(2, "AI Uprising")
    
    # 4. Run Ticks
    print("[2] Running 3 Ticks...")
    runtime.run_tick() # Tick 1
    
    # Check if influence objects initialized
    # Iterate all to find one
    has_inf = any(hasattr(u, "influence_score") for u in pop_engine.population)
    if has_inf:
        print("✅ SUCCESS: Influence attributes initialized on population.")
    else:
        print("❌ FAILURE: Influence attributes missing.")

    runtime.run_tick() # Tick 2 (Event Start)
    
    # Check active event
    if scheduler.active_events:
        print(f"✅ SUCCESS: Event active: {scheduler.active_events[0]['name']}")
    else:
        print("❌ FAILURE: Event did not start.")
        
    runtime.run_tick() # Tick 3
    
    print("[3] Integration Test Complete.")
    
    # Check for generated posts
    if len(social_net.new_posts) > 0:
        print(f"✅ SUCCESS: Generated {len(social_net.new_posts)} new posts.")
        print(f"   Sample: {social_net.new_posts[0]['content']}")
    else:
        print("⚠️ WARNING: No new posts generated. Check probabilities.")

if __name__ == "__main__":
    test_full_integration()
