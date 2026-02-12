"""
Simulation Rules Module

Defines all simulation rules that drive world state changes and event generation.
Rules are evaluated each simulation tick to determine state modifications and events.
"""

import random
from typing import List, Tuple, Dict, Any, Optional
from datetime import datetime

from core.state import WorldState
from core.events import Event, EventType


class SimulationRule:
    """Base class for defining simulation rules."""
    
    def __init__(self, name: str):
        self.name = name
    
    def update_parameter(self, param_name: str, value: Any) -> bool:
        """
        Update a rule parameter dynamically.
        
        Args:
            param_name: Name of parameter to update
            value: New value
            
        Returns:
            True if parameter was updated, False if not found
        """
        if hasattr(self, param_name):
            setattr(self, param_name, value)
            return True
        return False
    
    def get_parameters(self) -> Dict[str, Any]:
        """Get all public parameters (not starting with _)."""
        return {k: v for k, v in self.__dict__.items() if not k.startswith('_') and k != 'name'}
    
    def evaluate(self, state: WorldState) -> Tuple[List[Event], Dict[str, float]]:
        """
        Evaluate the rule against current world state.
        
        Returns:
            Tuple of (events_to_generate, metric_changes)
            - events_to_generate: List of Event objects
            - metric_changes: Dict mapping metric names to delta values
        """
        raise NotImplementedError("Subclasses must implement evaluate()")


class EconomyPressureRule(SimulationRule):
    """
    Rule: Economy Pressure
    IF water_price_index > 1.5
    THEN public_unrest += 0.1
    """
    
    def __init__(self):
        super().__init__("Economy Pressure")
        self.water_threshold = 1.5
        self.unrest_increase = 0.1
    
    def evaluate(self, state: WorldState) -> Tuple[List[Event], dict]:
        events = []
        changes = {}
        
        if state.water_price_index > self.water_threshold:
            changes['public_unrest'] = self.unrest_increase
            
            # Occasionally generate an economic event when this triggers
            if random.random() < 0.15:  # 15% chance
                event = Event(
                    event_type=EventType.RESOURCE_SHORTAGE,
                    date=state.current_date,
                    location="Neo Istanbul Water District",
                    scale=min(0.8, state.water_price_index - 1.0),
                    visibility=0.9,
                    description=f"Water prices reach {state.water_price_index:.2f}x baseline, causing public concern",
                    metadata={
                        'price_index': state.water_price_index,
                        'trigger': 'economy_pressure_rule'
                    }
                )
                events.append(event)
        
        return events, changes


class ProtestGenerationRule(SimulationRule):
    """
    Rule: Protest Generation (Probabilistic)
    IF public_unrest > 0.4
    THEN chance to generate protest event
    """
    
    def __init__(self):
        super().__init__("Protest Generation")
        self.unrest_threshold = 0.4
    
    def evaluate(self, state: WorldState) -> Tuple[List[Event], dict]:
        events = []
        changes = {}
        
        if state.public_unrest > self.unrest_threshold:
            # Probability increases with unrest level
            protest_probability = (state.public_unrest - self.unrest_threshold) * 0.5
            
            if random.random() < protest_probability:
                # Generate protest event
                protest_scale = min(0.9, state.public_unrest + random.uniform(-0.1, 0.2))
                
                locations = [
                    "Neo Istanbul Central Square",
                    "Tech District Plaza",
                    "Water Distribution Center",
                    "Corporate Sector Gateway"
                ]
                
                # Define event effects (feedback loop)
                event_effects = {
                    'media_trust': -0.05,  # Protests erode media trust
                    'corp_power_index': 0.03  # Corporations gain power during unrest
                }
                
                event = Event(
                    event_type=EventType.PROTEST,
                    date=state.current_date,
                    location=random.choice(locations),
                    scale=protest_scale,
                    visibility=0.8,
                    description=f"Citizens protest against rising costs and inequality",
                    metadata={
                        'unrest_level': state.public_unrest,
                        'participants_estimated': int(protest_scale * 10000),
                        'trigger': 'protest_generation_rule',
                        'effects_applied': event_effects,
                        'triggered_by_state': [f'public_unrest > {self.unrest_threshold}']
                    }
                )
                events.append(event)
                
                # Apply event feedback to world state
                state.apply_effect("protest_event", event_effects)
                
                # Protests slightly reduce unrest (release valve effect)
                changes['public_unrest'] = -0.05
        
        return events, changes


class CrisisEscalationRule(SimulationRule):
    """
    Rule: Crisis Escalation
    IF a protest event with scale > 0.6 was generated
    THEN generate political_crisis event
    """
    
    def __init__(self):
        super().__init__("Crisis Escalation")
        self.scale_threshold = 0.6
    
    def evaluate(self, state: WorldState, recent_events: List[Event] = None) -> Tuple[List[Event], dict]:
        """
        Evaluate crisis escalation based on recent protest events.
        
        Args:
            state: Current world state
            recent_events: Events generated this tick (to check for protests)
        """
        events = []
        changes = {}
        
        if recent_events is None:
            return events, changes
        
        # Check if any recent protests exceed the scale threshold
        large_protests = [
            e for e in recent_events 
            if e.type == EventType.PROTEST.value and e.scale > self.scale_threshold
        ]
        
        if large_protests:
            # Pick the largest protest
            largest_protest = max(large_protests, key=lambda e: e.scale)
            
            # Define crisis effects (feedback loop)
            crisis_effects = {
                'public_unrest': 0.15,  # Crises increase unrest
                'media_trust': -0.1,  # Media trust collapses
                'corp_power_index': 0.05  # Corps consolidate power
            }
            
            crisis_event = Event(
                event_type=EventType.POLITICAL_CRISIS,
                date=state.current_date,
                location=largest_protest.location,
                scale=min(0.95, largest_protest.scale + 0.1),
                visibility=1.0,  # Crises are highly visible
                description=f"Protest escalates into political crisis as authorities struggle to respond",
                metadata={
                    'triggered_by_protest': largest_protest.id,
                    'protest_scale': largest_protest.scale,
                    'trigger': 'crisis_escalation_rule',
                    'effects_applied': crisis_effects,
                    'triggered_by_state': [f'protest.scale > {self.scale_threshold}']
                }
            )
            events.append(crisis_event)
            
            # Apply crisis feedback to world state
            state.apply_effect("political_crisis_event", crisis_effects)
            
            # Note: We don't add these to 'changes' dict because
            # they're already applied via apply_effect (avoid double-counting)
        
        return events, changes


class NaturalDecayRule(SimulationRule):
    """
    Rule: Natural Decay
    Gradually returns extreme values toward baseline over time
    """
    
    def __init__(self):
        super().__init__("Natural Decay")
    
    def evaluate(self, state: WorldState) -> Tuple[List[Event], dict]:
        events = []
        changes = {}
        
        # Unrest naturally decreases slightly each day (people adapt)
        if state.public_unrest > 0.1:
            changes['public_unrest'] = -0.02
        
        # Price indices slowly drift back toward 1.0
        if state.water_price_index > 1.0:
            changes['water_price_index'] = -0.03
        
        if state.energy_price_index > 1.0:
            changes['energy_price_index'] = -0.02
        
        return events, changes


class RuleEngine:
    """Manages and evaluates all simulation rules."""
    
    def __init__(self):
        """Initialize the rule engine with all rules."""
        self.rules = [
            EconomyPressureRule(),
            ProtestGenerationRule(),
            NaturalDecayRule(),
            # Crisis escalation is handled separately as it needs recent events
        ]
        self.crisis_rule = CrisisEscalationRule()
    
    def get_rule(self, rule_name: str) -> Optional[SimulationRule]:
        """Get a rule by name."""
        if self.crisis_rule.name == rule_name:
            return self.crisis_rule
        
        for rule in self.rules:
            if rule.name == rule_name:
                return rule
        return None
    
    def apply_adjustment(self, adjustment: Dict[str, Any]) -> bool:
        """
        Apply an adjustment from the MetaObserver.
        
        Args:
            adjustment: Adjustment dictionary with rule_name, parameter, action, value
            
        Returns:
            True if adjustment was applied
        """
        rule_name = adjustment.get('rule_name')
        param_name = adjustment.get('parameter')
        action = adjustment.get('action')
        value = adjustment.get('value')
        limit = adjustment.get('limit')
        
        rule = self.get_rule(rule_name)
        if not rule:
            return False
        
        # Get current value
        if not hasattr(rule, param_name):
            return False
        
        current_value = getattr(rule, param_name)
        new_value = current_value
        
        # Calculate new value
        if action == 'increase':
            new_value += value
            if limit is not None:
                new_value = min(new_value, limit)
        elif action == 'decrease':
            new_value -= value
            if limit is not None:
                new_value = max(new_value, limit)
        elif action == 'set':
            new_value = value
            
        # Apply update
        if rule.update_parameter(param_name, new_value):
            print(f"   ⚖️  MetaObserver: Adjusted {rule_name}.{param_name} "
                  f"{current_value:.3f} -> {new_value:.3f} ({adjustment.get('reason')})")
            return True
        
        return False
    
    def apply_rules(self, state: WorldState) -> Tuple[List[Event], dict]:
        """
        Apply all rules to the current world state.
        
        Returns:
            Tuple of (all_events, all_metric_changes)
        """
        all_events = []
        all_changes = {}
        
        # Apply standard rules
        for rule in self.rules:
            events, changes = rule.evaluate(state)
            all_events.extend(events)
            
            # Accumulate metric changes
            for metric, delta in changes.items():
                all_changes[metric] = all_changes.get(metric, 0) + delta
        
        # Apply crisis escalation rule based on events generated this tick
        crisis_events, crisis_changes = self.crisis_rule.evaluate(state, all_events)
        all_events.extend(crisis_events)
        
        for metric, delta in crisis_changes.items():
            all_changes[metric] = all_changes.get(metric, 0) + delta
        
        return all_events, all_changes
