"""
Test ImpactPipeline class.
"""

import logging
import os
import shutil
from core.impact_pipeline import ImpactPipeline
from content.social_impact import SocialImpactProcessor
from content.social_interaction import CommentManager, ReplyManager
from core.state import WorldState

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')


def test_impact_pipeline():
    """Test ImpactPipeline execution."""
    print("=== Testing ImpactPipeline ===\n")
    
    # Setup test data directory
    test_dir = "data_test_impact"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Setup components
    social_impact_processor = SocialImpactProcessor()
    comment_manager = CommentManager(data_dir=test_dir)
    reply_manager = ReplyManager(data_dir=test_dir)
    
    # Create pipeline
    pipeline = ImpactPipeline(
        social_impact_processor=social_impact_processor,
        reply_manager=reply_manager,
        comment_manager=comment_manager
    )
    
    # Create world state with initial values
    world_state = WorldState({
        'public_unrest': 0.3,
        'information_noise': 0.1,
        'media_trust': 0.5,
        'surveillance_level': 0.2
    })
    initial_unrest = world_state.public_unrest
    initial_noise = world_state.information_noise
    
    print(f"Initial state:")
    print(f"  public_unrest: {initial_unrest:.3f}")
    print(f"  information_noise: {initial_noise:.3f}\n")
    
    # Create mock posts
    posts = [
        {"id": "post_1", "category": "political", "content": "Test political post"},
        {"id": "post_2", "category": "personal", "content": "Test personal post"},
    ]
    
    # Add some comments manually
    comment_manager.add_comment("post_1", "user_001", "This is unacceptable!")
    comment_manager.add_comment("post_1", "user_002", "Propaganda.")
    comment_manager.add_comment("post_2", "user_003", "Interesting.")
    
    print("Added 3 test comments\n")
    
    # Run pipeline
    affected_posts = ["post_1", "post_2"]
    
    print("Running impact pipeline...\n")
    pipeline.run(affected_posts, world_state, posts)
    
    # Check if world state changed
    final_unrest = world_state.public_unrest
    final_noise = world_state.information_noise
    
    print(f"\nFinal state:")
    print(f"  public_unrest: {final_unrest:.3f}")
    print(f"  information_noise: {final_noise:.3f}\n")
    
    unrest_changed = abs(final_unrest - initial_unrest) > 0.001
    noise_changed = abs(final_noise - initial_noise) > 0.001
    
    if unrest_changed or noise_changed:
        print("✅ World state was modified by social impact")
        print(f"  Δ unrest: {final_unrest - initial_unrest:+.3f}")
        print(f"  Δ noise: {final_noise - initial_noise:+.3f}")
    else:
        print("⚠️  World state unchanged (might be expected with neutral comments)")
    
    # Test with empty post list
    print("\n=== Testing Empty Post List ===\n")
    pipeline.run([], world_state, posts)
    print("✅ Handled empty post list gracefully\n")
    
    # Test with non-existent post
    print("=== Testing Non-Existent Post ===\n")
    pipeline.run(["post_999"], world_state, posts)
    print("✅ Handled non-existent post gracefully\n")
    
    print("=== All Tests Complete ===")


if __name__ == "__main__":
    test_impact_pipeline()
