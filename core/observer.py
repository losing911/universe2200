"""
Meta Observer Module

Tracks high-level simulation metrics and applies dynamic adjustments 
to maintain balance and narrative interest.
"""

import json
from pathlib import Path
from typing import Dict, Any, List
import statistics

from core.events import Event, EventType


class MetaObserver:
    """
    Observer system that monitors simulation health and narrative quality.
    
    Tracks:
    - Event Diversity: Variety of event types generated
    - Conflict Frequency: Rate of conflict events (protests, crises)
    - Market Instability: Volatility of economic indicators
    
    Applies deterministic adjustments to rules if thresholds are crossed.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize the observer.
        
        Args:
            data_dir: Path to data directory
        """
        if data_dir is None:
            project_root = Path(__file__).parent.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(data_dir)
            
        self.config_path = self.data_dir.parent / "config" / "observer_config.json"
        self.config = self._load_config()
        
        self.last_check_date = None
        self.observations = []
        self.pending_adjustments = []
    
    def _load_config(self) -> Dict[str, Any]:
        """Load observer configuration."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def observe(self, current_date, recent_events: List[Event], state_history: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze simulation state and generate adjustments if needed.
        
        Args:
            current_date: Current simulation date
            recent_events: List of events from the check period (e.g. last 7 days)
            state_history: List of state snapshots from check period
            
        Returns:
            List of adjustment dictionaries
        """
        if not self.config.get("enabled", False):
            return []
        
        adjustments = []
        metrics = self._calculate_metrics(recent_events, state_history)
        
        # Check thresholds
        thresholds = self.config.get("thresholds", {})
        
        # 1. Check Conflict Frequency
        if metrics['conflict_count'] > thresholds.get("max_conflict_frequency", 5):
            adj = self.config['adjustments'].get('reduce_conflict')
            if adj:
                adjustments.append(self._create_adjustment(adj, "High conflict detected"))
        
        # 2. Check Event Diversity
        elif metrics['diversity_score'] < thresholds.get("min_event_diversity", 2):
            # Only increase diversity if conflict isn't already high
            adj = self.config['adjustments'].get('increase_diversity')
            if adj:
                adjustments.append(self._create_adjustment(adj, "Low event diversity"))
                
        # 3. Check Market Instability
        if metrics['market_volatility'] > thresholds.get("max_market_instability", 0.1):
            adj = self.config['adjustments'].get('stabilize_market')
            if adj:
                adjustments.append(self._create_adjustment(adj, "Market instability detected"))
        
        # Log observation
        self.observations.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "metrics": metrics,
            "adjustments": adjustments
        })
        
        return adjustments

    def _calculate_metrics(self, events: List[Event], state_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate high-level metrics from raw data."""
        # Event counts
        event_types = set(e.type for e in events)
        conflict_types = {EventType.PROTEST.value, EventType.POLITICAL_CRISIS.value, "conflict"}
        conflict_count = sum(1 for e in events if e.type in conflict_types)
        
        # Market volatility (std dev of water price)
        water_prices = [s.get('water_price_index', 1.0) for s in state_history]
        if len(water_prices) > 1:
            volatility = statistics.stdev(water_prices)
        else:
            volatility = 0.0
            
        return {
            "diversity_score": len(event_types),
            "conflict_count": conflict_count,
            "market_volatility": round(volatility, 3),
            "total_events": len(events)
        }
    
    def _create_adjustment(self, config_adj: Dict[str, Any], reason: str) -> Dict[str, Any]:
        """Create a standardized adjustment object."""
        return {
            "rule_name": config_adj['target_rule'],
            "parameter": config_adj['parameter'],
            "action": config_adj['action'],
            "value": config_adj['value'],
            "limit": config_adj.get('min_limit') if config_adj['action'] == 'decrease' else config_adj.get('max_limit'),
            "reason": reason
        }
