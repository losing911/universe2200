"""
Content Generator Base Interface

Defines the abstract interface for content generation.
Implementations can use templates, AI models, or hybrid approaches.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any

from core.events import Event


class ContentGeneratorBase(ABC):
    """
    Abstract base class for content generators.
    
    Defines the interface that all content generators must implement.
    This allows the dispatcher to work with any generator implementation
    without knowing the specific details.
    """
    
    @abstractmethod
    def generate_news_content(self, event: Event) -> Dict[str, Any]:
        """
        Generate news content for ChronoNet platform.
        
        Args:
            event: Event to generate content from
            
        Returns:
            Dictionary with news content structure
        """
        pass
    
    @abstractmethod
    def generate_social_content(self, event: Event) -> Dict[str, Any]:
        """
        Generate social media content for MindLink platform.
        
        Args:
            event: Event to generate content from
            
        Returns:
            Dictionary with social media content structure
        """
        pass
    
    @abstractmethod
    def generate_video_content(self, event: Event) -> Dict[str, Any]:
        """
        Generate video content for NeoFlix platform.
        
        Args:
            event: Event to generate content from
            
        Returns:
            Dictionary with video content structure
        """
        pass
    
    @abstractmethod
    def generate_market_alert(self, event: Event) -> Dict[str, Any]:
        """
        Generate market alert for StellarExchange platform.
        
        Args:
            event: Event to generate content from
            
        Returns:
            Dictionary with market alert content structure
        """
        pass
