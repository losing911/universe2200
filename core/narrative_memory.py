"""
Narrative Memory Module

Tracks and remembers significant events in the universe.
Phase 1: Passive Memory - records patterns without affecting simulation.

This layer provides the foundation for future narrative intelligence where
the universe can recognize patterns and react to recurring situations.
"""

import json
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from core.events import Event


class NarrativeMemory:
    """
    Passive narrative memory system that records event patterns.
    
    For each unique event signature (type + location + involved_factions),
    tracks:
    - first_seen_date: When this pattern first occurred
    - last_seen_date: Most recent occurrence
    - occurrence_count: How many times it happened
    - last_severity: Most recent severity/scale
    
    Phase 1: No simulation effects - purely observational.
    """
    
    def __init__(self, data_dir: str = None):
        """
        Initialize narrative memory.
        
        Args:
            data_dir: Path to data directory
        """
        if data_dir is None:
            project_root = Path(__file__).parent.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.memory_file = self.data_dir / "narrative_memory.json"
        self.memories = {}
        self.load_memory()
    
    def generate_event_signature(self, event: Event) -> str:
        """
        Generate a unique signature for an event pattern.
        
        Signature includes:
        - Event type
        - Location
        - Involved factions (if any)
        
        Args:
            event: Event to generate signature for
            
        Returns:
            String signature (hash for consistency)
        """
        # Extract components
        event_type = event.type
        location = event.location
        
        # Extract factions from metadata if present
        metadata = event.metadata if hasattr(event, 'metadata') else {}
        factions = metadata.get('involved_factions', [])
        
        # Sort factions for consistency
        if isinstance(factions, list):
            factions = sorted(factions)
        else:
            factions = []
        
        # Create signature string
        signature_parts = [
            f"type:{event_type}",
            f"location:{location}",
            f"factions:{','.join(factions)}" if factions else "factions:none"
        ]
        signature_string = "|".join(signature_parts)
        
        # Hash for consistent length
        signature_hash = hashlib.md5(signature_string.encode()).hexdigest()[:16]
        
        return signature_hash
    
    def record_event(self, event: Event):
        """
        Record an event in narrative memory.
        
        Args:
            event: Event to record
        """
        # Generate signature
        signature = self.generate_event_signature(event)
        
        # Get event date
        event_date = event.date.strftime('%Y-%m-%d') if hasattr(event.date, 'strftime') else str(event.date)
        
        # Get severity/scale
        severity = event.scale if hasattr(event, 'scale') else 0.5
        
        # Check if this pattern exists in memory
        if signature in self.memories:
            # Update existing memory
            memory = self.memories[signature]
            memory['last_seen_date'] = event_date
            memory['occurrence_count'] += 1
            memory['last_severity'] = round(severity, 3)
        else:
            # Create new memory entry
            self.memories[signature] = {
                'signature': signature,
                'event_type': event.type,
                'location': event.location,
                'involved_factions': self._extract_factions(event),
                'first_seen_date': event_date,
                'last_seen_date': event_date,
                'occurrence_count': 1,
                'last_severity': round(severity, 3)
            }
    
    def _extract_factions(self, event: Event) -> List[str]:
        """Extract factions from event metadata."""
        metadata = event.metadata if hasattr(event, 'metadata') else {}
        factions = metadata.get('involved_factions', [])
        
        if isinstance(factions, list):
            return sorted(factions)
        return []
    
    def get_memory(self, signature: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific memory by signature.
        
        Args:
            signature: Event signature
            
        Returns:
            Memory entry or None
        """
        return self.memories.get(signature)
    
    def get_all_memories(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all stored memories.
        
        Returns:
            Dictionary of all memory entries
        """
        return self.memories.copy()
    
    def get_memories_by_location(self, location: str) -> List[Dict[str, Any]]:
        """
        Get all memories for a specific location.
        
        Args:
            location: Location to filter by
            
        Returns:
            List of memory entries
        """
        return [
            memory for memory in self.memories.values()
            if memory['location'] == location
        ]
    
    def get_memories_by_type(self, event_type: str) -> List[Dict[str, Any]]:
        """
        Get all memories for a specific event type.
        
        Args:
            event_type: Event type to filter by
            
        Returns:
            List of memory entries
        """
        return [
            memory for memory in self.memories.values()
            if memory['event_type'] == event_type
        ]
    
    def get_recurring_patterns(self, min_occurrences: int = 3) -> List[Dict[str, Any]]:
        """
        Get event patterns that have occurred multiple times.
        
        Args:
            min_occurrences: Minimum occurrence count
            
        Returns:
            List of recurring patterns
        """
        return [
            memory for memory in self.memories.values()
            if memory['occurrence_count'] >= min_occurrences
        ]
    
    def save_memory(self):
        """Save narrative memory to JSON file."""
        # Convert to list for JSON serialization
        memory_list = list(self.memories.values())
        
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(memory_list, f, indent=2, ensure_ascii=False)
    
    def load_memory(self):
        """Load narrative memory from JSON file."""
        if self.memory_file.exists():
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                memory_list = json.load(f)
            
            # Convert list to dictionary keyed by signature
            self.memories = {
                memory['signature']: memory
                for memory in memory_list
            }
        else:
            self.memories = {}
    
    def get_memory_summary(self) -> Dict[str, Any]:
        """
        Get a summary of narrative memory.
        
        Returns:
            Summary statistics
        """
        total_patterns = len(self.memories)
        total_occurrences = sum(m['occurrence_count'] for m in self.memories.values())
        
        # Find most common pattern
        most_common = None
        max_count = 0
        for memory in self.memories.values():
            if memory['occurrence_count'] > max_count:
                max_count = memory['occurrence_count']
                most_common = memory
        
        return {
            'total_unique_patterns': total_patterns,
            'total_event_occurrences': total_occurrences,
            'most_common_pattern': {
                'type': most_common['event_type'] if most_common else None,
                'location': most_common['location'] if most_common else None,
                'count': max_count
            } if most_common else None
        }
