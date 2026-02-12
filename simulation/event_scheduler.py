"""
Event Scheduler

Manages random and scheduled global events for Universe 2200.
Events include AI Uprisings, Sensor Leaks, and Economic Crashes.
"""

import random
from typing import Dict, Any, List, Optional
import copy

class EventScheduler:
    """
    Handles event triggering, duration tracking, and effect application.
    """
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.active_events = []  # List of dicts: {name, remaining_duration, effects...}
        self.scheduled_events = {} # Dict: tick -> list of event names
        self.history = []
        
        # Event Templates
        self.TEMPLATES = {
            "AI Uprising": {
                "name": "AI Uprising",
                "duration": 5,
                "effects": {
                    "public_unrest": 0.15,
                    "surveillance_level": 0.1,
                    "market_confidence": -0.2,
                    "ai_dependency": -0.1
                },
                "faction_mods": {"synthetic": 1.5, "bio": 0.5, "corporate": 0.8},
                "influence_mod": 1.2 # Chaos boosts influence gain
            },
            "Corporate Censorship": {
                "name": "Corporate Censorship",
                "duration": 3,
                "effects": {
                    "media_trust": -0.1,
                    "information_noise": -0.2,
                    "surveillance_level": 0.15
                },
                "faction_mods": {"corporate": 1.3, "activist": 0.7},
                "influence_mod": 0.5 # Harder to gain influence
            },
            "Data Leak": {
                "name": "Data Leak",
                "duration": 2,
                "effects": {
                    "media_trust": -0.2,
                    "privacy_index": -0.3, # unmapped metric? State should handle it gracefully
                    "public_unrest": 0.05
                },
                "faction_mods": {"activist": 1.4, "corporate": 0.6},
                "influence_mod": 1.5 # Leaks create opportunities
            },
            "Economic Crash": {
                "name": "Economic Crash",
                "duration": 4,
                "effects": {
                    "market_confidence": -0.4,
                    "public_unrest": 0.2,
                    "ai_dependency": 0.1 # People turn to algo trading/saving?
                },
                "faction_mods": {"corporate": 0.5},
                "influence_mod": 0.8
            },
            "Information Blackout": {
                "name": "Information Blackout",
                "duration": 2,
                "effects": {
                    "information_noise": -0.8,
                    "media_trust": -0.05,
                    "public_unrest": 0.1
                },
                "faction_mods": {}, # No one benefits easily
                "influence_mod": 0.1 # Very hard to reach people
            }
        }

    def schedule_event(self, tick: int, event_name: str):
        """Schedule a specific event for a future tick."""
        if tick not in self.scheduled_events:
            self.scheduled_events[tick] = []
        self.scheduled_events[tick].append(event_name)

    def trigger_event(self, event_name: str) -> Optional[Dict[str, Any]]:
        """Instantiate an event from a template."""
        if event_name in self.TEMPLATES:
            # Create a deep copy to track dynamic state
            event = copy.deepcopy(self.TEMPLATES[event_name])
            event["start_tick"] = -1 # Will be set by runtime or logic
            return event
        return None

    def check_for_events(self, tick: int) -> List[Dict[str, Any]]:
        """
        Check and trigger events for the current tick.
        Handles both scheduled events and random chance.
        
        Args:
            tick: Current simulation tick
        
        Returns:
            List of new event objects triggered this tick.
        """
        triggered = []
        
        # 1. Scheduled Events
        if tick in self.scheduled_events:
            for name in self.scheduled_events[tick]:
                evt = self.trigger_event(name)
                if evt:
                    evt["start_tick"] = tick
                    self.active_events.append(evt)
                    triggered.append(evt)
                    self.history.append(f"Tick {tick}: {name} started (Scheduled)")
        
        # 2. Random Events (Every N ticks, e.g., 20)
        # Using rng for determinism
        if tick % 20 == 0 and tick > 0:
            # 30% chance of random event
            if self.rng.random() < 0.3:
                # Pick random template
                keys = list(self.TEMPLATES.keys())
                name = self.rng.choice(keys)
                evt = self.trigger_event(name)
                if evt:
                    evt["start_tick"] = tick
                    self.active_events.append(evt)
                    triggered.append(evt)
                    self.history.append(f"Tick {tick}: {name} started (Random)")
                    
        return triggered

    def apply_event_effects(self, world_state: Any):
        """
        Apply active event effects to the world state.
        Manages duration and expiry.
        """
        active_now = []
        
        for event in self.active_events:
            # Decrease duration
            event["duration"] -= 1
            
            # Apply World Metrics Effects
            # Using verify-safe access to world_state
            if hasattr(world_state, "apply_effect"):
                # Construct safe dict
                effs = event.get("effects", {})
                world_state.apply_effect(f"Event: {event['name']}", effs)
            
            # Keep if duration > 0
            if event["duration"] > 0:
                active_now.append(event)
            else:
                self.history.append(f"{event['name']} ended")
        
        self.active_events = active_now

    def get_active_modifiers(self) -> Dict[str, Any]:
        """
        Aggregate modifiers from all active events.
        Useful for other engines (Influence, Faction).
        """
        mods = {
            "influence_mult": 1.0,
            "faction_mults": {}
        }
        
        for event in self.active_events:
            # Influence
            mods["influence_mult"] *= event.get("influence_mod", 1.0)
            
            # Factions
            f_mods = event.get("faction_mods", {})
            for faction, mult in f_mods.items():
                current = mods["faction_mults"].get(faction, 1.0)
                mods["faction_mults"][faction] = current * mult
                
        return mods
