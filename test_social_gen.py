"""
Test SocialMediaGenerator module.
"""

import json
from content.social_media_generator import SocialMediaGenerator

def test_generator():
    print("=== Social Media Generator Test ===\n")
    
    gen = SocialMediaGenerator()
    
    # Test Data
    metrics = {
        "public_unrest": 0.85,
        "media_trust": 0.15,
        "surveillance_level": 0.9,
        "information_noise": 0.7
    }
    
    news = [
        {"title": "Riots Continue in Sector 7", "summary": "Unrest growing..."}
    ]
    
    # Generate
    seed = 42
    output = gen.generate_feed(metrics, news, seed, count_range=(5, 5))
    
    print(f"Generated {len(output['posts'])} posts.")
    print("-" * 50)
    
    for post in output['posts']:
        print(f"[{post['author_type'].upper()}] ({post['tone']})")
        print(f"Content: {post['content']}")
        print(f"Engagement: {post['engagement']} | Sentiment: {post['sentiment']}")
        print("-" * 20)

    # Determinism Check
    print("\nDeterminism Check:")
    output2 = gen.generate_feed(metrics, news, seed, count_range=(5, 5))
    
    if output['posts'][0]['content'] == output2['posts'][0]['content']:
        print("✅ Success: Output is deterministic")
    else:
        print("❌ Failed: Output varies with same seed")

if __name__ == "__main__":
    test_generator()
