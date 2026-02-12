"""
World State Management Module

Manages the global state of the 2200 universe including economic, social, 
and political metrics that drive the simulation.
"""

from datetime import datetime, timedelta
from typing import Dict, Any


class WorldState:
    """
    Represents the global state of the universe.
    
    Attributes:
        water_price_index: Price index for water (can exceed 1.0)
        energy_price_index: Price index for energy (can exceed 1.0)
        public_unrest: Level of public unrest (0-1)
        media_trust: Public trust in media (0-1)
        ai_dependency: Society's dependency on AI (0-1)
        corp_power_index: Corporate power influence (0-1)
        current_date: Current simulation date
    """
    
    def __init__(self, state_data: Dict[str, Any]):
        """Initialize world state from dictionary."""
        self.water_price_index = state_data.get('water_price_index', 1.0)
        self.energy_price_index = state_data.get('energy_price_index', 1.0)
        self.public_unrest = state_data.get('public_unrest', 0.0)
        self.media_trust = state_data.get('media_trust', 0.5)
        self.ai_dependency = state_data.get('ai_dependency', 0.5)
        self.corp_power_index = state_data.get('corp_power_index', 0.5)
        
        # Content feedback metrics
        self.public_awareness = state_data.get('public_awareness', 0.5)
        self.public_sentiment = state_data.get('public_sentiment', 0.5)
        self.market_confidence = state_data.get('market_confidence', 0.5)
        self.information_noise = state_data.get('information_noise', 0.1)
        self.surveillance_level = state_data.get('surveillance_level', 0.5) # New: State monitoring intensity
        
        # Parse date string to datetime
        date_str = state_data.get('current_date', '2207-01-01')
        self.current_date = datetime.strptime(date_str, '%Y-%m-%d')
        
        # Track effects applied to this state (for traceability)
        self.last_effects = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert world state to dictionary for JSON serialization."""
        return {
            'water_price_index': round(self.water_price_index, 3),
            'energy_price_index': round(self.energy_price_index, 3),
            'public_unrest': round(self.public_unrest, 3),
            'media_trust': round(self.media_trust, 3),
            'ai_dependency': round(self.ai_dependency, 3),
            'corp_power_index': round(self.corp_power_index, 3),
            'public_awareness': round(self.public_awareness, 3),
            'public_sentiment': round(self.public_sentiment, 3),
            'public_sentiment': round(self.public_sentiment, 3),
            'market_confidence': round(self.market_confidence, 3),
            'information_noise': round(self.information_noise, 3),
            'surveillance_level': round(self.surveillance_level, 3),
            'current_date': self.current_date.strftime('%Y-%m-%d')
        }
    
    def advance_date(self, days: int = 1):
        """Advance the current date by specified number of days."""
        self.current_date += timedelta(days=days)
    
    def clamp_metric(self, value: float, min_val: float = 0.0, max_val: float = 1.0) -> float:
        """Clamp a metric value to valid range."""
        return max(min_val, min(max_val, value))
    
    def modify_metric(self, metric_name: str, delta: float):
        """
        Modify a metric by a delta value.
        
        Args:
            metric_name: Name of the metric to modify
            delta: Amount to change the metric by (can be negative)
        """
        current_value = getattr(self, metric_name)
        new_value = current_value + delta
        
        # Clamp most metrics to 0-1 range, except price indices which can exceed 1.0
        if 'price_index' in metric_name:
            new_value = max(0.0, new_value)  # Only prevent negative
        else:
            new_value = self.clamp_metric(new_value)
        
        setattr(self, metric_name, new_value)
    
    def get_metric(self, metric_name: str) -> float:
        """Get the value of a specific metric."""
        return getattr(self, metric_name)
    
    def apply_effect(self, source: str, effects: Dict[str, float]):
        """
        Apply metric changes with a traceable source.
        This enables events to affect the world state (feedback loop).
        
        Args:
            source: Description of what caused this effect (e.g., "protest_event")
            effects: Dictionary mapping metric names to delta values
        """
        applied = {}
        
        for metric, delta in effects.items():
            if hasattr(self, metric):
                # Apply the change using existing modify_metric logic
                old_value = getattr(self, metric)
                self.modify_metric(metric, delta)
                new_value = getattr(self, metric)
                
                # Track what actually changed (after clamping)
                actual_delta = new_value - old_value
                if abs(actual_delta) > 0.001:  # Only track meaningful changes
                    applied[metric] = actual_delta
        
        # Record this effect in history for traceability
        if applied:
            self.last_effects.append({
                "source": source,
                "effects": applied,
                "date": self.current_date.strftime('%Y-%m-%d')
            })
    
    def __str__(self) -> str:
        """String representation of world state."""
        return (
            f"WorldState(date={self.current_date.strftime('%Y-%m-%d')}, "
            f"water_price={self.water_price_index:.2f}, "
            f"unrest={self.public_unrest:.2f})"
        )




