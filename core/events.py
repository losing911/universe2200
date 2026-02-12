"""
Event System Module

Defines event structure and event generation for the simulation.
Events are the primary output of the simulation engine.
"""

from datetime import datetime
from typing import Dict, Any, List
from enum import Enum
import uuid


class EventType(Enum):
    """Enumeration of possible event types."""
    PROTEST = "protest"
    POLITICAL_CRISIS = "political_crisis"
    ECONOMIC_SHIFT = "economic_shift"
    CORPORATE_ACTION = "corporate_action"
    MEDIA_INCIDENT = "media_incident"
    AI_INCIDENT = "ai_incident"
    RESOURCE_SHORTAGE = "resource_shortage"


class CanonLevel(Enum):
    """Canon level indicates how 'official' an event is."""
    SOFT = "soft"  # May be retconned or refined
    HARD = "hard"  # Confirmed canon
    ABSOLUTE = "absolute"  # Core universe facts


class Event:
    """
    Represents a single event in the universe timeline.
    
    Required fields:
        id: Unique event identifier
        type: Type of event (from EventType enum)
        date: When the event occurred
        location: Where the event occurred
        scale: Magnitude/impact of event (0-1)
        visibility: How visible/known the event is (0-1)
        canon_level: How established this event is in canon
        generated_by: What system generated this event
    """
    
    def __init__(
        self,
        event_type: EventType,
        date: datetime,
        location: str,
        scale: float,
        visibility: float,
        description: str = "",
        canon_level: CanonLevel = CanonLevel.SOFT,
        generated_by: str = "simulation_engine",
        metadata: Dict[str, Any] = None
    ):
        """Initialize a new event."""
        self.id = str(uuid.uuid4())
        self.type = event_type.value if isinstance(event_type, EventType) else event_type
        self.date = date
        self.location = location
        self.scale = max(0.0, min(1.0, scale))  # Clamp to 0-1
        self.visibility = max(0.0, min(1.0, visibility))  # Clamp to 0-1
        self.description = description
        self.canon_level = canon_level.value if isinstance(canon_level, CanonLevel) else canon_level
        self.generated_by = generated_by
        self.metadata = metadata or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary for JSON serialization."""
        return {
            'id': self.id,
            'type': self.type,
            'date': self.date.strftime('%Y-%m-%d'),
            'location': self.location,
            'scale': round(self.scale, 3),
            'visibility': round(self.visibility, 3),
            'description': self.description,
            'canon_level': self.canon_level,
            'generated_by': self.generated_by,
            'metadata': self.metadata
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'Event':
        """Create an Event from dictionary data."""
        event = Event(
            event_type=data['type'],
            date=datetime.strptime(data['date'], '%Y-%m-%d'),
            location=data['location'],
            scale=data['scale'],
            visibility=data['visibility'],
            description=data.get('description', ''),
            canon_level=data.get('canon_level', 'soft'),
            generated_by=data.get('generated_by', 'simulation_engine'),
            metadata=data.get('metadata', {})
        )
        event.id = data['id']  # Preserve original ID
        return event
    
    def __str__(self) -> str:
        """String representation of event."""
        return (
            f"Event({self.type} at {self.location} on {self.date.strftime('%Y-%m-%d')}, "
            f"scale={self.scale:.2f})"
        )


class EventLog:
    """Manages the event log for the simulation."""
    
    def __init__(self, events_data: List[Dict[str, Any]] = None):
        """Initialize event log with optional existing events."""
        self.events: List[Event] = []
        
        if events_data:
            self.events = [Event.from_dict(e) for e in events_data]
    
    def add_event(self, event: Event):
        """Add a new event to the log."""
        self.events.append(event)
    
    def get_events_by_type(self, event_type: EventType) -> List[Event]:
        """Get all events of a specific type."""
        type_str = event_type.value if isinstance(event_type, EventType) else event_type
        return [e for e in self.events if e.type == type_str]
    
    def get_events_by_date(self, date: datetime) -> List[Event]:
        """Get all events on a specific date."""
        return [e for e in self.events if e.date.date() == date.date()]
    
    def to_list(self) -> List[Dict[str, Any]]:
        """Convert all events to list of dictionaries."""
        return [e.to_dict() for e in self.events]
