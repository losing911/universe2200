"""
Real-Time Simulation Engine

Provides a continuous, drift-corrected clock for the Universe 2200 simulation.
Manages the main loop and coordinates tick handlers.
"""

import time
import logging
from typing import List, Callable, Optional

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealTimeEngine:
    """
    Core clock for real-time simulation logic.
    Runs a continuous loop calling registered handlers at fixed intervals.
    """
    
    def __init__(self, tick_rate_hz: float = 1.0):
        """
        Args:
            tick_rate_hz: Target ticks per second (default 1.0)
        """
        self.tick_rate = tick_rate_hz
        self.tick_duration = 1.0 / tick_rate_hz
        self.running = False
        self.tick_count = 0
        self.handlers: List[Callable[[int, float], None]] = []
        
    def register_tick_handler(self, handler: Callable[[int, float], None]):
        """
        Register a callback to be executed on every tick.
        Handler signature: (tick_count: int, delta_time: float) -> None
        """
        self.handlers.append(handler)
        logger.info(f"Registered tick handler: {handler.__name__}")

    def start(self):
        """Start the simulation loop (Blocking)."""
        if self.running:
            return
            
        self.running = True
        logger.info("RealTimeEngine started.")
        
        # Drift correction variables
        next_tick = time.monotonic()
        
        try:
            while self.running:
                current_time = time.monotonic()
                delta = current_time - (next_tick - self.tick_duration)
                
                # Execute Handlers
                for handler in self.handlers:
                    try:
                        handler(self.tick_count, delta)
                    except Exception as e:
                        logger.error(f"Error in handler {handler.__name__}: {e}")
                
                self.tick_count += 1
                
                # Schedule next tick with drift correction
                next_tick += self.tick_duration
                sleep_time = next_tick - time.monotonic()
                
                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    # We are running behind, don't sleep
                    # Optionally warn if lagging significantly
                    if sleep_time < -1.0:
                        logger.warning(f"Engine lagging by {-sleep_time:.2f}s")
                        # Reset clock to prevent burst catch-up
                        next_tick = time.monotonic()
                        
        except KeyboardInterrupt:
            logger.info("Simulation interrupted by user.")
            self.stop()
            
    def stop(self):
        """Stop the simulation loop."""
        self.running = False
        logger.info("RealTimeEngine stopped.")
