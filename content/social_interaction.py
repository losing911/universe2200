"""
Social Interaction Layer

Manages user comments and AI-generated replies for social media posts.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

# We'll treat NarrativeMemory and WorldState as external dependencies passed in
# to keep this module decoupled.

class CommentManager:
    """
    Manages storage and retrieval of social media comments.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the comment manager.
        
        Args:
            data_dir: Path to data directory (default: ../data relative to project root)
        """
        if data_dir is None:
            # Get the data directory relative to the project
            project_root = Path(__file__).parent.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.comments_file = self.data_dir / "social_comments.json"
        self.comments_db = self._load_comments()
        
    def _load_comments(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load comments from JSON file."""
        if self.comments_file.exists():
            try:
                with open(self.comments_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
        
    def save_comments(self):
        """Save comments to JSON file."""
        with open(self.comments_file, 'w', encoding='utf-8') as f:
            json.dump(self.comments_db, f, indent=2, ensure_ascii=False)
            
    def add_comment(self, post_id: str, user_handle: str, content: str) -> Dict[str, Any]:
        """
        Add a user comment to a post.
        
        Args:
            post_id: ID of the post being commented on
            user_handle: Username of the commenter
            content: Text content of the comment
            
        Returns:
            The created comment object
        """
        comment = {
            "id": f"cmt_{int(datetime.now().timestamp())}_{random.randint(100, 999)}",
            "post_id": post_id,
            "user_handle": user_handle,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "type": "user_comment"
        }
        
        if post_id not in self.comments_db:
            self.comments_db[post_id] = []
            
        self.comments_db[post_id].append(comment)
        self.save_comments()
        return comment
        
    def get_comments_for_post(self, post_id: str) -> List[Dict[str, Any]]:
        """Get all comments for a specific post."""
        return self.comments_db.get(post_id, [])


class SocialReplyGenerator:
    """
    Generates AI replies to user comments on social media posts.
    
    Replies are impersonal, atmospheric, and represent the "mood" of the universe
    or institutional responses, never direct conversation.
    """
    
    def __init__(self):
        # Stub for LLM connection
        pass
        
    def generate_reply(self, 
                      post: Dict[str, Any], 
                      comments: List[Dict[str, Any]], 
                      world_state: Dict[str, Any],
                      narrative_memory: Any = None) -> Optional[Dict[str, Any]]:
        """
        Generate an AI reply based on the post context and user comments.
        
        Args:
            post: The original social media post
            comments: List of user comments on the post
            world_state: Current state of the world (metrics)
            narrative_memory: (Optional) Access to historical event patterns
            
        Returns:
            Reply object or None if no reply is generated
        """
        # Context gathering
        context = {
            "post_content": post.get("content", ""),
            "post_topic": post.get("topics", []),
            "recent_comments": [c["content"] for c in comments[-3:]], # Look at last 3 comments
            "unrest_level": world_state.get("public_unrest", 0.0),
            "media_trust": world_state.get("media_trust", 0.5)
        }
        
        # Determine if we should reply (not every comment needs a reply)
        # For this implementation, we'll force a reply if there are comments
        if not comments:
            return None
            
        # Generate text
        reply_text = self._generate_text(context)
        
        # Create reply object
        reply = {
            "id": f"ai_reply_{int(datetime.now().timestamp())}",
            "post_id": post.get("id", "unknown"),
            "user_handle": "System_Observer", # Or "Network_Admin", "City_OS"
            "content": reply_text,
            "timestamp": datetime.now().isoformat(),
            "type": "ai_reply",
            "is_system_message": True
        }
        
        return reply

    def _generate_text(self, context: Dict[str, Any]) -> str:
        """
        Abstracted LLM call to generate reply text.
        
        TODO: Connect to real LLM backend.
        
        Input Context:
        - Post content
        - User comments
        - World metrics (unrest, trust)
        
        Expected Output:
        - Short, cryptic, or bureaucratic text.
        - No direct address ("Hey user...").
        - Themes: Surveillance, entropy, corporate detachment, subtle warnings.
        """
        # Placeholder logic for "In-Universe" feel
        unrest = context["unrest_level"]
        comments_text = " ".join(context["recent_comments"]).lower()
        
        if unrest > 0.7:
            if "riot" in comments_text or "anger" in comments_text:
                return "⚠️ NOTICE: Civic gathering protocols are in effect. Disperse immediately."
            else:
                return "System Alert: High network traffic detected in your sector. Bandwidth limited."
                
        elif context["media_trust"] < 0.3:
            return "Content Flagged: Unverified information source. Proceed with caution."
            
        else:
            options = [
                "Index updated. Pattern recognized.",
                "Observation recorded.",
                "The network is listening.",
                "Your feedback has been aggregated.",
                "Data point archived."
            ]
            return random.choice(options)


class ReplyManager:
    """
    Manages storage and retrieval of AI-generated replies.
    Only allows ONE active AI reply per post.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the reply manager.
        
        Args:
            data_dir: Path to data directory (default: ../data relative to project root)
        """
        if data_dir is None:
            # Get the data directory relative to the project
            project_root = Path(__file__).parent.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.replies_file = self.data_dir / "social_replies.json"
        self.replies_db = self._load_replies()
        
    def _load_replies(self) -> Dict[str, Dict[str, Any]]:
        """Load replies from JSON file. Returns dict of post_id -> reply_obj"""
        if self.replies_file.exists():
            try:
                with open(self.replies_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                return {}
        return {}
        
    def save_replies(self):
        """Save replies to JSON file."""
        with open(self.replies_file, 'w', encoding='utf-8') as f:
            json.dump(self.replies_db, f, indent=2, ensure_ascii=False)
            
    def save_reply(self, post_id: str, reply_obj: Dict[str, Any]):
        """
        Save an AI reply for a post.
        Overwrites any existing reply for this post.
        
        Args:
            post_id: ID of the post
            reply_obj: The reply object (dict)
        """
        self.replies_db[post_id] = reply_obj
        self.save_replies()
        
    def get_reply(self, post_id: str) -> Optional[Dict[str, Any]]:
        """Get the active AI reply for a post."""
        return self.replies_db.get(post_id)
