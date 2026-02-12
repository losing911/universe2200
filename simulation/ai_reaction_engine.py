"""
AI Reaction Engine

Decides how AI entities (e.g., system monitors, corporate bots) react 
to user posts based on influence, reputation, and world state.
"""

import hashlib
import random
from typing import Dict, Any, Tuple

class AIReactionEngine:
    """
    Determines AI responses: Support, Attack, Ignore, Manipulate.
    """
    
    # Reaction Types
    REACTION_SUPPORT = "support"
    REACTION_ATTACK = "attack"
    REACTION_IGNORE = "ignore"
    REACTION_MANIPULATE = "manipulate"

    def decide_reaction(self, 
                       ai_entity: Dict[str, Any], 
                       target_entity: Dict[str, Any], 
                       post: Dict[str, Any], 
                       world_state: Dict[str, float]) -> Dict[str, Any]:
        """
        determine the AI's reaction to a specific post by a user.
        
        Args:
            ai_entity: The AI actor (dict with faction_loyalty, chaos_affinity, etc.)
            target_entity: The user who posted (dict with influence_score, etc.)
            post: The content being reacted to (dict with id, topics)
            world_state: Current simulation metrics
            
        Returns:
            Dict containing:
            - reaction_type: support, attack, ignore, manipulate
            - entity_deltas: changes to target's influence/reputation
            - world_deltas: changes to global metrics
            - reason: debug string explanation
        """
        
        # 1. Deterministic Seed
        # Combine IDs to create a unique seed for this interaction
        post_id = post.get("id", "unknown")
        ai_id = ai_entity.get("id", "ai_system")
        target_id = target_entity.get("id", "unknown_user")
        
        seed_str = f"{post_id}_{ai_id}_{target_id}"
        seed_int = int(hashlib.sha256(seed_str.encode()).hexdigest(), 16)
        rng = random.Random(seed_int)
        
        # 2. Extract Metrics
        ai_chaos = ai_entity.get("chaos_affinity", 0.0)
        ai_factions = ai_entity.get("faction_loyalty", {})
        
        target_inf = target_entity.get("influence_score", 0.0)
        target_rep = target_entity.get("reputation_score", 0.0)
        target_faction = target_entity.get("faction", "neutral")
        
        unrest = world_state.get("public_unrest", 0.0)
        
        # 3. Calculate Base Probability Scores
        
        # A. Faction Alignment
        # If AI has loyalty to target's faction, boost support
        faction_alignment = ai_factions.get(target_faction, 0.0)
        # Scale: 0.0 (neutral) to 1.0 (loyal)
        
        # B. Threat Assessment
        # High influence + low reputation = Threat (Attack/Manipulate)
        # High influence + high reputation = Ally (Support/Manipulate)
        is_high_influence = target_inf > 50.0
        is_reputable = target_rep > 20.0
        is_notorious = target_rep < -20.0
        
        # 4. Determine Reaction Weights
        # Default Weights
        w_support = 0.1
        w_attack = 0.1
        w_manipulate = 0.05
        w_ignore = 0.75 # Default implies ignore is most common
        
        # Modify based on Faction
        if faction_alignment > 0.6:
            w_support += 0.4
            w_ignore -= 0.3
        elif faction_alignment < 0.2 and target_faction != "neutral":
             # Low alignment or opposing? Assuming 0-1 scale means 0 is neutral/opposed depending on implementation
             # If using signed alignment, 0 is neutral. But dict usually implies specific loyalty.
             # If target faction is present in loyalty dict but low, maybe just ignoring.
             # If NOT present, treated as 0.
             pass
             
        # Modify based on Reputation
        if is_reputable:
            w_support += 0.2
            w_attack -= 0.1
        elif is_notorious:
            w_attack += 0.3
            w_support -= 0.1
            
        # Modify based on Chaos Affinity (AI Personality)
        if ai_chaos > 0.7:
            w_manipulate += 0.3
            w_ignore -= 0.1
            # Chaotic AI likes to attack high influence targets
            if is_high_influence:
                w_attack += 0.2
        
        # Modify based on World State
        if unrest > 0.8:
            # High unrest makes AI more reactive (crackdown or exploitation)
            w_ignore -= 0.2
            w_attack += 0.1
            w_manipulate += 0.1

        # Normalize Weights (simple clamping 0, ensure sum > 0)
        weights = {
            self.REACTION_SUPPORT: max(0.01, w_support),
            self.REACTION_ATTACK: max(0.01, w_attack),
            self.REACTION_MANIPULATE: max(0.01, w_manipulate),
            self.REACTION_IGNORE: max(0.01, w_ignore)
        }
        
        # 5. Select Reaction
        reaction_type = rng.choices(
            list(weights.keys()),
            weights=list(weights.values()),
            k=1
        )[0]
        
        # 6. Calculate Effects
        entity_deltas = {}
        world_deltas = {}
        
        if reaction_type == self.REACTION_SUPPORT:
            # Boost target
            entity_deltas["influence_score"] = 0.5 + (target_inf * 0.01)
            entity_deltas["reputation_score"] = 1.0
            # Slight calm
            world_deltas["public_unrest"] = -0.005
            
        elif reaction_type == self.REACTION_ATTACK:
            # Hurt target
            entity_deltas["influence_score"] = -0.5 - (target_inf * 0.02) # Higher inf = harder fall
            entity_deltas["reputation_score"] = -2.0
            # Increase unrest/noise
            world_deltas["public_unrest"] = 0.01
            world_deltas["information_noise"] = 0.05
            
        elif reaction_type == self.REACTION_MANIPULATE:
            # Mixed bag
            entity_deltas["influence_score"] = 1.0 # Boost visibility
            entity_deltas["reputation_score"] = -1.0 # But sow doubt
            entity_deltas["chaos_affinity"] = 0.05
            # Confusion
            world_deltas["media_trust"] = -0.01
            world_deltas["information_noise"] = 0.1
            
        # Ignore has no effect
        
        return {
            "reaction_type": reaction_type,
            "entity_deltas": entity_deltas,
            "world_deltas": world_deltas,
            "reason": f"Weights: {weights}" # Debug
        }
