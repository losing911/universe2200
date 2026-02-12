"""
Test ActivityPipeline class.
"""

import logging
import os
import shutil
from core.activity_pipeline import ActivityPipeline
from core.tick_context import TickContext
from simulation.population_engine import PopulationEngine
from content.social_interaction import CommentManager

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')


def test_activity_pipeline():
    """Test ActivityPipeline execution."""
    print("=== Testing ActivityPipeline ===\n")
    
    # Setup test data directory
    test_dir = "data_test_pipeline"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Setup components
    population_engine = PopulationEngine(size=100, seed=42)
    comment_manager = CommentManager(data_dir=test_dir)
    
    # Create pipeline (without social network for simplicity)
    pipeline = ActivityPipeline(
        population_engine=population_engine,
        comment_manager=comment_manager,
        social_network=None
    )
    
    # Create tick context
    tick_ctx = TickContext(base_seed=42, tick_number=1, mode="simulation")
    
    # Mock world state
    world_state = {
        "date": "2207-01-01",
        "public_unrest": 0.3,
        "media_trust": 0.5,
        "surveillance_level": 0.2
    }
    
    # Mock posts
    posts = [
        {"id": "post_1", "category": "tech", "content": "Test post 1"},
        {"id": "post_2", "category": "personal", "content": "Test post 2"},
    ]
    
    # Run pipeline
    print(f"Running pipeline for tick {tick_ctx.tick_number}")
    print(f"Tick seed: {tick_ctx.tick_seed}\n")
    
    affected_posts = pipeline.run(tick_ctx, world_state, posts)
    
    print(f"\n✅ Pipeline completed")
    print(f"Affected posts: {affected_posts}")
    print(f"Number of posts affected: {len(affected_posts)}\n")
    
    # Test determinism - run again with same tick context
    print("=== Testing Determinism ===\n")
    
    tick_ctx_2 = TickContext(base_seed=42, tick_number=1, mode="simulation")
    affected_posts_2 = pipeline.run(tick_ctx_2, world_state, posts)
    
    if affected_posts == affected_posts_2:
        print("✅ Deterministic: Same tick_seed produces same affected posts")
    else:
        print("❌ Non-deterministic: Different affected posts")
        print(f"  First run: {affected_posts}")
        print(f"  Second run: {affected_posts_2}")
    
    # Test different tick
    print("\n=== Testing Tick Progression ===\n")
    
    tick_ctx_3 = TickContext(base_seed=42, tick_number=2, mode="simulation")
    affected_posts_3 = pipeline.run(tick_ctx_3, world_state, posts)
    
    print(f"Tick 2 affected posts: {affected_posts_3}")
    print(f"Different from tick 1: {affected_posts != affected_posts_3}")
    
    print("\n=== All Tests Complete ===")


if __name__ == "__main__":
    test_activity_pipeline()
