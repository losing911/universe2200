"""
Universe 2200 Runtime Configuration

Defines configuration parameters for the simulation runtime.
"""

from dataclasses import dataclass
from typing import Literal


@dataclass
class RuntimeConfig:
    """
    Configuration for Universe 2200 Runtime.
    
    Attributes:
        mode: Runtime mode - "simulation" for pure simulation, "hybrid" for real users + simulation
        tick_interval_seconds: Time between simulation ticks (seconds)
        base_seed: Base random seed for deterministic behavior
        enable_ai_replies: Whether AI generates replies to posts/comments
        enable_social_impact: Whether social activity affects world state
        enable_real_users: Whether to allow real user participation
        max_posts_per_tick: Maximum posts to process per tick
        max_comments_per_tick: Maximum comments to process per tick
    """
    
    mode: str = "simulation"
    tick_interval_seconds: int = 3
    base_seed: int = 42
    enable_ai_replies: bool = True
    enable_social_impact: bool = True
    enable_real_users: bool = False
    max_posts_per_tick: int = 20
    max_comments_per_tick: int = 5000
    
    # AI Configuration
    ai_provider: str = "openai"  # openai, openrouter, anthropic
    ai_model: str = "gpt-4o-mini"
    ai_api_key: str = ""
    ai_base_url: str = ""  # Optional, for OpenRouter or Local LLM
    
    def validate(self) -> None:
        """
        Validate configuration parameters.
        
        Raises:
            ValueError: If any configuration parameter is invalid
        """
        valid_modes = {"simulation", "hybrid"}
        
        if self.mode not in valid_modes:
            raise ValueError(
                f"Invalid mode '{self.mode}'. Must be one of: {', '.join(valid_modes)}"
            )
        
        if self.tick_interval_seconds < 0:
            raise ValueError("tick_interval_seconds must be non-negative (0 = manual mode)")
        
        if self.max_posts_per_tick <= 0:
            raise ValueError("max_posts_per_tick must be positive")
        
        if self.max_comments_per_tick <= 0:
            raise ValueError("max_comments_per_tick must be positive")
        
        if self.enable_ai_replies and not self.ai_api_key:
            # Check env var if not in config
            import os
            if not os.getenv("LLM_API_KEY"):
                # Warning only, don't crash
                pass
