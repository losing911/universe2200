"""
Tick Context for Universe 2200

Encapsulates tick-level state and deterministic seed for all subsystems.
"""

from datetime import datetime
from typing import Dict, Any


class TickContext:
    """
    Context object passed to all subsystems during tick execution.
    
    Guarantees tick-level determinism and reproducibility by providing
    a computed tick_seed based on base_seed + tick_number.
    
    Attributes:
        tick_number: Current tick number (incremental)
        tick_seed: Deterministic seed for this tick (base_seed + tick_number)
        timestamp: When this tick was created
        mode: Runtime mode ("simulation" or "hybrid")
    """
    
    def __init__(self, base_seed: int, tick_number: int, mode: str):
        """
        Initialize tick context.
        
        Args:
            base_seed: Base random seed
            tick_number: Current tick number
            mode: Runtime mode
        """
        self.tick_number = tick_number
        self.tick_seed = base_seed + tick_number
        self.timestamp = datetime.now()
        self.mode = mode
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert tick context to dictionary.
        
        Returns:
            Dictionary representation of tick context
        """
        return {
            "tick_number": self.tick_number,
            "tick_seed": self.tick_seed,
            "timestamp": self.timestamp.isoformat(),
            "mode": self.mode
        }
