
import json
import os
from collections import Counter
from datetime import datetime
from pathlib import Path

# Trend Analysis Logic
def analyze_trends(limit=10):
    """
    Analyze recent posts to find trending topics/keywords/hashtags.
    Returns a list of trend objects.
    """
    social_file = Path("data/public/public_social_x.json") # or join both x and insta
    if not social_file.exists():
        return []
        
    try:
        with open(social_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            posts = data.get("data", [])
    except Exception:
        return []
        
    # Simple Frequency Analysis
    # 1. Extract hashtags
    # 2. Extract capitalized phrases (Named Entities - rough proxy)
    
    hashtags = []
    keywords = []
    
    stop_words = {"The", "A", "In", "On", "Of", "For", "To", "Is", "Are", "And", "Or", "But"}
    
    for post in posts:
        content = post.get("content", "")
        words = content.split()
        
        for w in words:
            if w.startswith("#") and len(w) > 2:
                hashtags.append(w)
            elif w[0].isupper() and w.isalpha() and w not in stop_words and len(w) > 3:
                keywords.append(w.strip(".,!?"))
                
    # Count
    tag_counts = Counter(hashtags)
    kw_counts = Counter(keywords)
    
    trends = []
    
    # Top 5 Hashtags
    for tag, count in tag_counts.most_common(5):
        trends.append({
            "topic": tag,
            "volume": f"{count * 120} posts", # Fake volume multiplier for realism
            "category": "Hashtag"
        })
        
    # Top 5 Keywords
    for kw, count in kw_counts.most_common(5):
        trends.append({
            "topic": kw,
            "volume": f"{count * 85} posts",
            "category": "Trending"
        })
        
    return trends[:limit]

if __name__ == "__main__":
    print(json.dumps(analyze_trends(), indent=2))
