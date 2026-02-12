from content.social_interaction import CommentManager, SocialReplyGenerator, ReplyManager
import json
import os

# Setup mock data context
world_state = {
    "public_unrest": 0.8,
    "media_trust": 0.2
}

post = {
    "id": "post_123",
    "content": "Water prices are insane! We need to march on the distribution center.",
    "topics": ["water", "protest"]
}

# 1. Test Comment Manager
print("--- Testing Comment Manager ---")
cm = CommentManager()
# Clear any existing test file
if os.path.exists(cm.comments_file):
    os.remove(cm.comments_file)
    cm = CommentManager() # Re-init

print(f"Adding comment to post {post['id']}...")
c1 = cm.add_comment(post["id"], "user_citizen_1", "I'm with you! Enough is enough.")
print(f"Comment added: {c1['content']}")

c2 = cm.add_comment(post["id"], "user_citizen_2", "Be careful, the drones are watching.")
print(f"Comment added: {c2['content']}")

loaded_comments = cm.get_comments_for_post(post["id"])
print(f"Loaded {len(loaded_comments)} comments from storage.")
assert len(loaded_comments) == 2

# 2. Test AI Reply Generation and Persistence
print("\n--- Testing AI Reply Generator & Persistence ---")
generator = SocialReplyGenerator()
rm = ReplyManager()
# Clear existing replies
if os.path.exists(rm.replies_file):
    os.remove(rm.replies_file)
    rm = ReplyManager()

print(f"World State: Unrest={world_state['public_unrest']}, Trust={world_state['media_trust']}")
reply = generator.generate_reply(post, loaded_comments, world_state)

if reply:
    print(f"AI Reply Generated: {reply['content']}")
    print(f"Reply Type: {reply['type']}")
    
    # Save reply
    print("Saving reply to storage...")
    rm.save_reply(post["id"], reply)
    
    # Verify persistence
    saved_reply = rm.get_reply(post["id"])
    assert saved_reply is not None
    assert saved_reply["content"] == reply["content"]
    print("✅ Persistence Verified: Reply saved and loaded correctly.")
    
    # Test Overwrite
    print("Testing overwrite with new reply...")
    new_reply = reply.copy()
    new_reply["content"] = "OVERWRITTEN: New system status."
    rm.save_reply(post["id"], new_reply)
    
    updated_reply = rm.get_reply(post["id"])
    assert updated_reply["content"] == "OVERWRITTEN: New system status."
    print("✅ Overwrite Verified: Old reply replaced.")

else:
    print("No reply generated.")

