"""
World Management Module

Handles loading and saving of world state, characters, and events from/to JSON files.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List

from .state import WorldState
from .characters import CharacterManager
from .events import EventLog


class WorldManager:
    """
    Manages the entire world state including state metrics, characters, and events.
    Handles persistence to/from JSON files.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize WorldManager.
        
        Args:
            data_dir: Path to data directory (default: ../data relative to this file)
        """
        if data_dir is None:
            # Get the data directory relative to this file
            current_dir = Path(__file__).parent.parent
            self.data_dir = current_dir / "data"
        else:
            self.data_dir = Path(data_dir)
        
        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Define file paths
        self.state_file = self.data_dir / "world_state.json"
        self.characters_file = self.data_dir / "characters.json"
        self.events_file = self.data_dir / "event_log.json"
        
        # Initialize components
        self.state: WorldState = None
        self.characters: CharacterManager = None
        self.events: EventLog = None
    
    def initialize_default_state(self) -> Dict[str, Any]:
        """Create default initial world state."""
        return {
            'water_price_index': 1.6,  # Above threshold to trigger economy pressure
            'energy_price_index': 1.2,
            'public_unrest': 0.3,  # Close to protest threshold
            'media_trust': 0.4,
            'ai_dependency': 0.6,
            'corp_power_index': 0.7,
            'current_date': '2207-01-01'
        }
    
    def load_world(self):
        """Load all world data from JSON files."""
        # Load world state
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                state_data = json.load(f)
        else:
            state_data = self.initialize_default_state()
            self._save_json(self.state_file, state_data)
        
        self.state = WorldState(state_data)
        
        # Load characters
        if self.characters_file.exists():
            with open(self.characters_file, 'r', encoding='utf-8') as f:
                characters_data = json.load(f)
        else:
            characters_data = []
            self._save_json(self.characters_file, characters_data)
        
        self.characters = CharacterManager(characters_data)
        
        # Load events
        if self.events_file.exists():
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
        else:
            events_data = []
            self._save_json(self.events_file, events_data)
        
        self.events = EventLog(events_data)
    
    def save_world(self):
        """Save all world data to JSON files."""
        # Save world state
        state_dict = self.state.to_dict()
        self._save_json(self.state_file, state_dict)
        
        # Save characters
        characters_list = self.characters.to_list()
        self._save_json(self.characters_file, characters_list)
        
        # Save events
        events_list = self.events.to_list()
        self._save_json(self.events_file, events_list)
    
    def _save_json(self, file_path: Path, data: Any):
        """Save data to JSON file with pretty formatting."""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of current world state."""
        return {
            'date': self.state.current_date.strftime('%Y-%m-%d'),
            'metrics': {
                'water_price_index': self.state.water_price_index,
                'energy_price_index': self.state.energy_price_index,
                'public_unrest': self.state.public_unrest,
                'media_trust': self.state.media_trust,
                'ai_dependency': self.state.ai_dependency,
                'corp_power_index': self.state.corp_power_index
            },
            'num_characters': len(self.characters.characters),
            'num_events': len(self.events.events)
        }
