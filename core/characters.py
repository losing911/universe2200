"""
Character Models Module

Defines character entities within the 2200 universe.
Currently a placeholder for future character-based simulation.
"""

from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class Character:
    """
    Represents a character in the 2200 universe.
    
    Attributes:
        id: Unique character identifier
        name: Character name
        role: Character's role in society (e.g., "activist", "corp_exec", "politician")
        influence: Character's influence level (0-1)
        location: Character's current location
        faction: Which faction/organization they belong to
    """
    id: str
    name: str
    role: str
    influence: float
    location: str
    faction: str = "independent"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'name': self.name,
            'role': self.role,
            'influence': round(self.influence, 3),
            'location': self.location,
            'faction': self.faction
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Character':
        """Create a Character from dictionary data."""
        return Character(
            id=data['id'],
            name=data['name'],
            role=data['role'],
            influence=data.get('influence', 0.5),
            location=data['location'],
            faction=data.get('faction', 'independent')
        )


class CharacterManager:
    """Manages all characters in the simulation."""
    
    def __init__(self, characters_data: List[Dict[str, Any]] = None):
        """Initialize character manager with optional character data."""
        self.characters: List[Character] = []
        
        if characters_data:
            self.characters = [Character.from_dict(c) for c in characters_data]
    
    def add_character(self, character: Character):
        """Add a new character to the simulation."""
        self.characters.append(character)
    
    def get_character(self, character_id: str) -> Character:
        """Get a character by ID."""
        for char in self.characters:
            if char.id == character_id:
                return char
        return None
    
    def get_characters_by_role(self, role: str) -> List[Character]:
        """Get all characters with a specific role."""
        return [c for c in self.characters if c.role == role]
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convert all characters to list of dictionaries."""
        return [c.to_dict() for c in self.characters]
