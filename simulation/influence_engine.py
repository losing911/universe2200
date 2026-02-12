"""
Influence Engine

Tracks and updates entity influence, reputation, and loyalty scores.
Used for both User and AI personas.
"""

from typing import Dict, Any, List, Optional
import math

class InfluenceEngine:
    """
    Manages influence, reputation, and alignment metrics for entities.
    """
    
    # Constants for Limits
    MIN_INFLUENCE = 0.0
    MAX_INFLUENCE = 100.0
    
    MIN_REPUTATION = -100.0
    MAX_REPUTATION = 100.0
    
    MIN_METRIC = 0.0
    MAX_METRIC = 1.0
    
    def __init__(self):
        # Could hold internal history if needed, but stateless for now
        pass

    def calculate_influence_delta(self, 
                                entity: Dict[str, Any], 
                                engagement_data: Dict[str, Any], 
                                world_state: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate changes to entity metrics based on recent activity.
        
        Args:
            entity: The user/AI entity object (dict)
            engagement_data: Data about recent engagement (comments, replies, likes)
            world_state: Current state of the world
            
        Returns:
            Dictionary of metric deltas {metric_name: delta_value}
        """
        deltas = {
            "influence_score": 0.0,
            "reputation_score": 0.0,
            "chaos_affinity": 0.0,
            "trust_alignment": 0.0
        }
        
        # 1. Influence based on Engagement Volume
        # More comments/replies -> Higher Visibility -> Higher Influence
        num_comments = engagement_data.get("comments", 0)
        num_replies = engagement_data.get("replies", 0)
        total_interactions = num_comments + num_replies
        
        # Logarithmic growth for influence to prevent runaway values
        if total_interactions > 0:
            influence_gain = math.log(total_interactions + 1, 10) * 0.5
            deltas["influence_score"] += influence_gain
            
        # 2. Reputation based on AI Interaction
        # Check for AI sentiment in replies
        # We assume engagement_data includes a summary or list of AI replies
        ai_replies = engagement_data.get("ai_replies", [])
        
        for reply in ai_replies:
            content = reply.get("content", "").lower()
            
            # AI Opposition (Warnings, Alerts) -> Reputation Hit
            if any(k in content for k in ["violation", "alert", "warning", "illegal", "sanction"]):
                deltas["reputation_score"] -= 2.0
                deltas["trust_alignment"] -= 0.05
                
            # AI Support (Validation, Archive) -> Slight Reputation Boost
            elif any(k in content for k in ["verified", "approved", "valid", "compliant"]):
                deltas["reputation_score"] += 1.0
                deltas["trust_alignment"] += 0.02
                
        # 3. World Metrics Impact
        # High Unrest amplifies Chaos Affinity changes
        public_unrest = world_state.get("public_unrest", 0.0)
        media_trust = world_state.get("media_trust", 0.5)
        
        # If user is highly active during unrest, chaos affinity increases
        if public_unrest > 0.6 and total_interactions > 5:
            deltas["chaos_affinity"] += 0.01 * (public_unrest * 2)
            
        # If media trust is low, trust alignment drops faster
        if media_trust < 0.3:
            deltas["trust_alignment"] -= 0.01

        return deltas

    def apply_influence(self, entity: Dict[str, Any], deltas: Dict[str, float]) -> Dict[str, Any]:
        """
        Apply calculated deltas to the entity's state.
        Clamps values within valid ranges.
        
        Args:
            entity: The entity to update (modified in-place)
            deltas: The changes to apply
            
        Returns:
            The modified entity
        """
        # Ensure entity has default fields if missing
        self._ensure_fields(entity)
        
        # Apply Deltas
        for metric, delta in deltas.items():
            if metric in entity:
                # Special handling for different ranges
                if metric == "influence_score":
                    new_val = entity[metric] + delta
                    entity[metric] = max(self.MIN_INFLUENCE, min(self.MAX_INFLUENCE, new_val))
                    
                elif metric == "reputation_score":
                    new_val = entity[metric] + delta
                    entity[metric] = max(self.MIN_REPUTATION, min(self.MAX_REPUTATION, new_val))
                    
                elif metric in ["chaos_affinity", "trust_alignment"]:
                    new_val = entity[metric] + delta
                    entity[metric] = max(self.MIN_METRIC, min(self.MAX_METRIC, new_val))
                    
                # Handle faction loyalty separately if it was a dict? 
                # The requirements listed faction_loyalty as a dict, but didn't specify delta logic for it.
                # Assuming delta keys might come in as "faction_loyalty.faction_name" later.
                
        return entity

    def decay_influence(self, entity: Dict[str, Any], rate: float = 0.05):
        """
        Apply natural decay to influence over time.
        Reflects fading relevance.
        
        Args:
            entity: The entity to update
            rate: Decay amount (fixed or percentage)
        """
        self._ensure_fields(entity)
        
        # Simple linear decay for now, clamped at 0
        # If entity has very high influence, maybe percentage decay?
        # Let's use small percentage decay for scaling
        
        current = entity["influence_score"]
        if current > 0:
            # Drop by 1% + fixed small amount
            decay_amount = (current * 0.01) + rate
            entity["influence_score"] = max(self.MIN_INFLUENCE, current - decay_amount)

    def _ensure_fields(self, entity: Dict[str, Any]):
        """Helper to initialize missing fields with defaults."""
        if "influence_score" not in entity: entity["influence_score"] = 0.0
        if "reputation_score" not in entity: entity["reputation_score"] = 0.0
        if "chaos_affinity" not in entity: entity["chaos_affinity"] = 0.0
        if "trust_alignment" not in entity: entity["trust_alignment"] = 0.5
        if "faction_loyalty" not in entity: entity["faction_loyalty"] = {}
