"""
User Management System

Handles user registration, authentication, and state management for real human users.
Designed for high scalability and integration with the Influence Engine.
"""

from typing import Dict, Any, Optional, List
import datetime
import hashlib

class UserEntity:
    """
    Represents a real human user in the simulation.
    """
    def __init__(self, 
                 user_id: str, 
                 username: str, 
                 faction: str = "neutral"):
        
        self.user_id = user_id
        self.username = username
        self.faction = faction
        
        # Metrics
        self.influence_score = 10.0  # Start with basic influence
        self.reputation_score = 0.0
        self.chaos_affinity = 0.0
        self.trust_alignment = 0.5
        
        # Metadata
        self.created_at = datetime.datetime.now()
        self.last_active = self.created_at
        
        # Extended attributes (for future use)
        self.achievements = []
        self.inventory = {}

    def to_dict(self) -> Dict[str, Any]:
        """Serialize user data."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "faction": self.faction,
            "influence_score": self.influence_score,
            "reputation_score": self.reputation_score,
            "chaos_affinity": self.chaos_affinity,
            "trust_alignment": self.trust_alignment,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat()
        }

    def update_metrics(self, deltas: Dict[str, float]):
        """Apply metric changes directly."""
        # Simple application, clamping should be handled by InfluenceEngine logic
        # But we can add safety clamps here too if needed.
        # For now, just apply.
        if "influence_score" in deltas:
            self.influence_score += deltas["influence_score"]
        if "reputation_score" in deltas:
            self.reputation_score += deltas["reputation_score"]
        if "chaos_affinity" in deltas:
            self.chaos_affinity += deltas["chaos_affinity"]
        if "trust_alignment" in deltas:
            self.trust_alignment += deltas["trust_alignment"]


class UserManager:
    """
    Manages user lifecycle and persistence.
    Current implementation uses in-memory storage (dict).
    """
    
    def __init__(self, influence_engine=None):
        # Storage: user_id -> UserEntity
        self.users: Dict[str, UserEntity] = {}
        # Index: username -> user_id (for quick lookup)
        self.username_index: Dict[str, str] = {}
        
        self.influence_engine = influence_engine

    def register_user(self, username: str, faction: str = "neutral") -> Optional[UserEntity]:
        """
        Register a new user.
        Returns the UserEntity or None if username exists.
        """
        if username in self.username_index:
            return None # Already exists
            
        # Generate ID (simple hash for now, or UUID)
        user_id = hashlib.sha256(f"{username}_{datetime.datetime.now().timestamp()}".encode()).hexdigest()[:16]
        
        new_user = UserEntity(user_id, username, faction)
        
        # Store
        self.users[user_id] = new_user
        self.username_index[username] = user_id
        
        return new_user

    def authenticate_user(self, username: str) -> Optional[UserEntity]:
        """
        Simulate authentication. 
        In strict mode, would check password hash.
        """
        user_id = self.username_index.get(username)
        if user_id:
            user = self.users[user_id]
            user.last_active = datetime.datetime.now()
            return user
        return None

    def get_user(self, user_id: str) -> Optional[UserEntity]:
        """Retrieve user by ID."""
        return self.users.get(user_id)

    def update_user_metrics(self, user_id: str, engagement_data: Dict[str, Any], world_state: Dict[str, Any]):
        """
        Calculate and apply metric updates via InfluenceEngine.
        """
        user = self.get_user(user_id)
        if not user or not self.influence_engine:
            return
            
        # Convert user to dict for engine (as engine expects dict)
        user_dict = user.to_dict()
        
        # Calculate deltas
        deltas = self.influence_engine.calculate_influence_delta(user_dict, engagement_data, world_state)
        
        # Apply deltas using helper or engine
        # Engine's apply_influence modifies the dict in place.
        # We need to map back to object.
        updated_dict = self.influence_engine.apply_influence(user_dict, deltas)
        
        # Update object
        user.influence_score = updated_dict["influence_score"]
        user.reputation_score = updated_dict["reputation_score"]
        user.chaos_affinity = updated_dict["chaos_affinity"]
        user.trust_alignment = updated_dict["trust_alignment"]
        
        # Update faction loyalty if present in updated_dict?
        # InfluenceEngine adds defaults if missing.
        
        return deltas

    def get_user_count(self) -> int:
        return len(self.users)
