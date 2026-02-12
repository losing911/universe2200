"""
Test ReplyPipeline class.
"""

import logging
import os
import shutil
from core.reply_pipeline import ReplyPipeline
from content.social_interaction import ReplyManager, CommentManager, SocialReplyGenerator

# Enable logging
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')


def test_reply_pipeline():
    """Test ReplyPipeline execution."""
    print("=== Testing ReplyPipeline ===\n")
    
    # Setup test data directory
    test_dir = "data_test_reply"
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    os.makedirs(test_dir)
    
    # Setup components
    reply_generator = SocialReplyGenerator()
    reply_manager = ReplyManager(data_dir=test_dir)
    comment_manager = CommentManager(data_dir=test_dir)
    
    # Create pipeline
    pipeline = ReplyPipeline(
        reply_generator=reply_generator,
        reply_manager=reply_manager,
        comment_manager=comment_manager
    )
    
    # Create mock posts
    posts = [
        {
            "id": "post_1",
            "category": "political",
            "content": "The new policies are concerning.",
            "author_id": "user_001"
        },
        {
            "id": "post_2",
            "category": "personal",
            "content": "Just had a great day!",
            "author_id": "user_002"
        },
    ]
    
    # Mock world state
    world_state = {
        "date": "2207-01-01",
        "public_unrest": 0.5,
        "media_trust": 0.4,
        "information_noise": 0.3
    }
    
    # Add comments to post_1 only
    comment_manager.add_comment("post_1", "user_100", "This is unacceptable!")
    comment_manager.add_comment("post_1", "user_101", "Propaganda.")
    
    print("Added 2 comments to post_1\n")
    
    # Run pipeline
    affected_posts = ["post_1", "post_2"]  # post_2 has no comments
    
    print("Running reply pipeline...\n")
    replied_posts = pipeline.run(affected_posts, posts, world_state)
    
    print(f"\n✅ Pipeline completed")
    print(f"Replied to posts: {replied_posts}")
    print(f"Number of replies generated: {len(replied_posts)}\n")
    
    # Verify reply was created for post_1
    if "post_1" in replied_posts:
        print("✅ Reply generated for post_1 (which had comments)")
        reply = reply_manager.get_reply("post_1")
        if reply:
            print(f"   Reply content: {reply.get('content', 'N/A')[:80]}...")
    else:
        print("❌ No reply generated for post_1")
    
    # Verify no reply for post_2
    if "post_2" not in replied_posts:
        print("✅ No reply for post_2 (which had no comments)")
    else:
        print("❌ Unexpected reply for post_2")
    
    # Test idempotency - run again, should not create duplicate
    print("\n=== Testing Idempotency ===\n")
    replied_posts_2 = pipeline.run(affected_posts, posts, world_state)
    
    if len(replied_posts_2) == 0:
        print("✅ No duplicate replies created (idempotent)")
    else:
        print(f"⚠️  Generated {len(replied_posts_2)} replies on second run")
    
    # Test with empty list
    print("\n=== Testing Empty Post List ===\n")
    replied_posts_empty = pipeline.run([], posts, world_state)
    print(f"✅ Handled empty list: {len(replied_posts_empty)} replies")
    
    # Test with non-existent post
    print("\n=== Testing Non-Existent Post ===\n")
    replied_posts_missing = pipeline.run(["post_999"], posts, world_state)
    print(f"✅ Handled non-existent post: {len(replied_posts_missing)} replies")
    
    print("\n=== All Tests Complete ===")


if __name__ == "__main__":
    test_reply_pipeline()
