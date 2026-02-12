"""
Social Impact Layer

Analyzes the impact of social media activity (posts, comments, AI replies)
on the global world state. Translate signals into metric changes.
"""

import math
from typing import Dict, List, Optional, Any
from datetime import datetime

class SocialImpactProcessor:
    """
    Quantifies the effect of social interactions on WorldState metrics.
    Deterministic, rule-based, and loggable.
    """
    
    # Maximum change allowed per cycle to prevent instability
    MAX_DELTA = 0.05
    
    def __init__(self):
        # Impact Configuration
        self.WEIGHTS = {
            "comment_vol": 0.0002,     # Noise per comment
            "sentiment": 0.005,        # Impact per sentiment signal
            "ai_auth": 0.01,           # Impact of authoritarian AI
            "ai_generic": 0.002,       # Impact of generic AI
        }

        self.UNREST_KEYWORDS = {
            "riot", "burn", "fight", "march", "protest", "resist", "liar", "fake", "down with"
        }
        self.CALM_KEYWORDS = {
            "wait", "see", "calm", "trust", "hope", "plan", "listen", "patience"
        }
        self.DISTRUST_KEYWORDS = {
            "propaganda", "bot", "fake", "censored", "watched", "drone", "shill", "coverup"
        }
        
    def apply_impact(self, 
                    post: Dict[str, Any], 
                    comments: List[Dict[str, Any]], 
                    ai_reply: Optional[Dict[str, Any]],
                    world_state: Any) -> Any:
        """
        Analyze social signals and apply changes directly to WorldState.
        
        Args:
            post: The original post
            comments: List of user comments
            ai_reply: The AI reply object (if any)
            world_state: The WorldState object (modified in-place)
            
        Returns:
            The modified WorldState object
        """
        # Defensive validation
        if not hasattr(world_state, 'apply_effect'):
            raise ValueError("Invalid world_state object: missing apply_effect method.")

        if not comments and not ai_reply:
            return world_state
            
        # Timestamp for potential future logging/event correlation
        current_ts = datetime.now().isoformat()
            
        # 1. Calculate Signals
        metrics_delta = self._calculate_deltas(comments, ai_reply)
        
        # 2. Apply to WorldState using its traceability method
        # Build a source description
        source_desc = f"social_impact:{post.get('id', 'unknown')[:8]}"
        
        world_state.apply_effect(source_desc, metrics_delta)
        
        # 3. Log the impact (Console for now, could be file later)
        # TODO: Integrate with a proper structured logger using current_ts
        if metrics_delta:
            print(f"   📉 Social Impact ({source_desc}): {metrics_delta}")
            
        return world_state

    def _calculate_deltas(self, comments: List[Dict[str, Any]], ai_reply: Optional[Dict[str, Any]]) -> Dict[str, float]:
        """Internal logic to derive metric changes from signals."""
        delta = {
            "public_unrest": 0.0,
            "media_trust": 0.0,
            "information_noise": 0.0,
            "surveillance_level": 0.0
        }
        
        # A. Volume Impact
        # High volume usually indicates high noise/attention
        num_comments = len(comments)
        delta["information_noise"] += num_comments * self.WEIGHTS["comment_vol"]
        
        # B. Sentiment Analysis
        unrest_signal = 0
        calm_signal = 0
        distrust_signal = 0
        
        for comment in comments:
            text = comment.get("content", "").lower()
            
            if self._has_keyword(text, self.UNREST_KEYWORDS):
                unrest_signal += 1
            if self._has_keyword(text, self.CALM_KEYWORDS):
                calm_signal += 1
            if self._has_keyword(text, self.DISTRUST_KEYWORDS):
                distrust_signal += 1
        
        # Apply sentiment weights
        # Unrest raises tension; Calm lowers it (but half as effectively)
        delta["public_unrest"] += (unrest_signal * self.WEIGHTS["sentiment"])
        delta["public_unrest"] -= (calm_signal * self.WEIGHTS["sentiment"] * 0.5)
        
        # Distrust lowers media trust and raises paranoia (surveillance level)
        delta["media_trust"] -= (distrust_signal * self.WEIGHTS["sentiment"])
        delta["surveillance_level"] += (distrust_signal * self.WEIGHTS["sentiment"] * 0.2) 
        
        # C. AI Reply Impact
        if ai_reply:
            reply_text = ai_reply.get("content", "").lower()
            
            # Authoritarian / Surveillance / Warning context
            # Effect: People are scared (unrest up) but quiet down (noise down)
            if self._has_keyword(reply_text, {"alert", "protocol", "violation", "detected", "monitor"}):
                delta["public_unrest"] += (self.WEIGHTS["ai_auth"] * 0.5) 
                delta["surveillance_level"] += self.WEIGHTS["ai_auth"]
                delta["information_noise"] -= 0.01 
                
            # Generic / Bureaucratic context
            # Effect: People feel ignored/processed (trust down), chatter continues (noise up)
            elif self._has_keyword(reply_text, {"logged", "archived", "processed", "ticket"}):
                delta["media_trust"] -= self.WEIGHTS["ai_generic"]
                delta["information_noise"] += 0.001
            
            # Else: Standard system engagement just adds to the noise floor
            else:
                 delta["information_noise"] += 0.001

        # Viral Amplification
        # Scale impact based on post volume (logarithmic)
        # viral_factor = log10(comments + 1) + 1
        # 0 comments -> 1.0x
        # 9 comments -> 2.0x
        # 99 comments -> 3.0x
        viral_factor = math.log(len(comments) + 1, 10) + 1
        
        for k in delta:
            delta[k] *= viral_factor

        # D. Normalize/Clamp Deltas
        # Critical to prevent runaway feedback loops from a single viral post
        for k in delta:
            if delta[k] > self.MAX_DELTA: delta[k] = self.MAX_DELTA
            if delta[k] < -self.MAX_DELTA: delta[k] = -self.MAX_DELTA
            
            # Clean up tiny floating point noise
            if abs(delta[k]) < 0.0001: delta[k] = 0.0
            
        # Filter out zero deltas to keep logs clean and reduce storage churn
        return {k: v for k, v in delta.items() if v != 0.0}

    def _has_keyword(self, text: str, keywords: set) -> bool:
        """Helper to safely check for keyword presence."""
        # Simple substring check is fast and deterministic
        return any(k in text for k in keywords)
