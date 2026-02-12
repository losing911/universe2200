"""
Social Network Core

Persistent state manager for the simulation's social graph.
Handles user storage, content persistence, and deterministic timeline generation.
"""

import json
import os
import random
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime

class SocialNetworkCore:
    """
    Core engine for the social network simulation.
    Manages persistent state of users and content.
    """
    
    DATA_DIR = "data"
    USERS_FILE = "social_users.json"
    CONTENT_FILE = "social_content.json"
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users_path = os.path.join(data_dir, self.USERS_FILE)
        self.content_path = os.path.join(data_dir, self.CONTENT_FILE)
        
        # In-memory Simulation State
        self.users: Dict[str, Dict[str, Any]] = {}
        self.posts: List[Dict[str, Any]] = []
        self.comments: List[Dict[str, Any]] = []
        self.daily_engagement: Dict[str, int] = {}
        
        # Ensure data directory exists
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Load existing state if available
        self.load_state()

    def load_state(self):
        """Load users and content from JSON files."""
        if os.path.exists(self.users_path):
            try:
                with open(self.users_path, 'r', encoding='utf-8') as f:
                    self.users = json.load(f)
            except Exception as e:
                print(f"Error loading users: {e}")
                self.users = {}
                
        if os.path.exists(self.content_path):
            try:
                with open(self.content_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.posts = data.get("posts", [])
                    self.comments = data.get("comments", [])
            except Exception as e:
                print(f"Error loading content: {e}")
                self.posts = []
                self.comments = []

    def save_state(self):
        """Persist current state to JSON files."""
        try:
            with open(self.users_path, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2)
                
            with open(self.content_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "posts": self.posts,
                    "comments": self.comments
                }, f, indent=2)
        except Exception as e:
            print(f"Error saving state: {e}")

    def ingest_population(self, population_users: List[Any]):
        """
        Ingest UserProfile objects from PopulationEngine.
        Idempotent: Updates existing users or creates new ones.
        """
        for p_user in population_users:
            user_id = p_user.user_id
            
            if user_id not in self.users:
                # Initialize new social user
                self.users[user_id] = {
                    "id": user_id,
                    "faction": p_user.faction,
                    "joined_date": datetime.now().strftime("%Y-%m-%d"),
                    "followers_count": self._calculate_initial_followers(p_user),
                    "clout_score": 0.1,  # 0.0 to 1.0 (Influence)
                    "lifetime_posts": 0,
                    "lifetime_comments": 0,
                    "topic_affinity": p_user.topic_affinity
                }
            else:
                # Update dynamic fields that might change in population engine
                # e.g., if topic affinity evolves
                self.users[user_id]["topic_affinity"] = p_user.topic_affinity

    def _calculate_initial_followers(self, p_user: Any) -> int:
        """Determinstic follower count based on user attributes."""
        # Simple deterministic hash-based "random" for consistency
        h = int(hashlib.sha256(p_user.user_id.encode()).hexdigest(), 16)
        
        # Power law distribution simulation
        # Most have 10-200, some have 1000+, very few 10k+
        base = h % 100
        multiplier = 1
        
        if (h % 10) == 0: multiplier = 10     # 10% chance -> 100-1000
        if (h % 100) == 0: multiplier = 100   # 1% chance -> 1000-10000
        if (h % 1000) == 0: multiplier = 1000 # 0.1% chance -> 10k+
        
        # Activity level boosts followers
        activity_boost = 1.0 + p_user.activity_level
        
        return int((50 + base) * multiplier * activity_boost)

    def register_post(self, post_data: Dict[str, Any]):
        """Register a new post into the system."""
        # Ensure required fields
        if "id" not in post_data:
            post_data["id"] = f"post_{len(self.posts)}_{int(datetime.now().timestamp())}"
        
        if "timestamp" not in post_data:
            post_data["timestamp"] = datetime.now().isoformat()
            
        if "metrics" not in post_data:
            post_data["metrics"] = {"likes": 0, "shares": 0, "comments": 0, "views": 0}
            
        self.posts.append(post_data)
        
        # Update user stats if author exists
        author_id = post_data.get("author_id")
        if author_id and author_id in self.users:
            self.users[author_id]["lifetime_posts"] += 1
            # Posting increases clout slightly
            self.users[author_id]["clout_score"] = min(1.0, self.users[author_id]["clout_score"] + 0.01)

    def register_comment(self, comment_data: Dict[str, Any]):
        """Register a comment and update engagement metrics."""
        self.comments.append(comment_data)
        
        # Update engagement for the target post
        post_id = comment_data.get("post_id")
        
        # Track daily engagement for viral logic
        self.daily_engagement[post_id] = self.daily_engagement.get(post_id, 0) + 1
        
        # Update User Stats
        user_id = comment_data.get("user_id")
        if user_id and user_id in self.users:
            self.users[user_id]["lifetime_comments"] += 1

    def register_reaction(self, reaction_data: Dict[str, Any]):
        """Register a like/reaction."""
        post_id = reaction_data.get("post_id")
        # Just track daily engagement; we don't store every like individually in MVP
        self.daily_engagement[post_id] = self.daily_engagement.get(post_id, 0) + 1
        
        # Permanent metric update happens in end_of_day, but we can update 'likes' here 
        # if we want real-time accuracy, but batching is better for perf.
        # However, for consistency with register_comment:
        # We don't have a 'reactions' list to append to (too big).
        # We just rely on daily_engagement -> end_of_day clamping.
        pass

    def register_repost(self, repost_data: Dict[str, Any]):
        """Register a repost/share."""
        post_id = repost_data.get("post_id")
        self.daily_engagement[post_id] = self.daily_engagement.get(post_id, 0) + 2 # Repost counts double?
        
        user_id = repost_data.get("user_id")
        if user_id and user_id in self.users:
             # Reposting creates content effectively
             self.users[user_id]["lifetime_posts"] += 1

    def get_timeline(self, user_id: str, world_state: Dict[str, Any], limit: int = 20) -> List[Dict[str, Any]]:
        """
        Generate a deterministic timeline for a specific user.
        Selects posts based on:
        - Recency (only recent posts considered)
        - Viral Score (global engagement)
        - Topic Affinity (user preference)
        - Influencer Weight (author clout)
        """
        user = self.users.get(user_id)
        if not user:
            return []
            
        # 1. Deterministic RNG
        date_str = str(world_state.get("date", "default_date"))
        seed_str = f"{user_id}_{date_str}_timeline"
        seed_val = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16) % (2**32)
        rng = random.Random(seed_val)
        
        # 2. Candidate Selection (Simplify: Take last 100 posts)
        candidates = self.posts[-100:] if self.posts else []
        if not candidates:
            return []
            
        # 3. Score Candidates
        scored_posts = []
        for post in candidates:
            score = 0.0
            p_metrics = post.get("metrics", {})
            p_id = post.get("id")
            
            # A. Base Score (Random Noise)
            score += rng.random() * 0.2
            
            # B. Topic Affinity lookup
            # Map post types/topics to affinity keys
            topic = post.get("topic", post.get("category", "general"))
            affinity = user["topic_affinity"].get(topic, 0.5) 
            score += affinity * 2.0  # Strong weight on affinity
            
            # C. Virtual Engagement (Viral Lift)
            # Use current daily engagement + historical metrics
            current_buzz = self.daily_engagement.get(p_id, 0)
            historical_buzz = p_metrics.get("likes", 0) + p_metrics.get("comments", 0)
            viral_score = (current_buzz * 0.5) + (historical_buzz * 0.05)
            # Logarithmic dampening or clamping usually better, but simple linear for now
            score += min(5.0, viral_score * 0.2)
            
            # D. Influencer Weight
            author_id = post.get("author_id")
            if author_id and author_id in self.users:
                clout = self.users[author_id].get("clout_score", 0.0)
                score += clout * 1.5
                
            scored_posts.append((score, post))
            
        # 4. Sort and Slice
        # Sort by score descending
        scored_posts.sort(key=lambda x: x[0], reverse=True)
        
        # Return top N
        return [item[1] for item in scored_posts[:limit]]

    def end_of_day_cleanup(self):
        """
        Consolidate daily metrics and save state.
        Call this at the end of every simulation tick.
        """
        # 1. Apply daily engagement to permanent metrics
        for post in self.posts:
            p_id = post.get("id")
            if p_id in self.daily_engagement:
                new_comments = self.daily_engagement[p_id]
                # Update comment count
                if "metrics" not in post:
                     post["metrics"] = {"likes": 0, "shares": 0, "comments": 0, "views": 0}
                
                post["metrics"]["comments"] += new_comments
                # Simulate likes/views correlation
                post["metrics"]["views"] += new_comments * 20
                post["metrics"]["likes"] += new_comments * 2
        
        # 2. Reset daily counter
        self.daily_engagement = {}
        
        # 3. Save
        self.save_state()
