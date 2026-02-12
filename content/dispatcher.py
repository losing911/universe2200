"""
Content Dispatcher Module

Receives simulation events and dispatches them to appropriate content generators.
Uses interface-based design to support multiple generator implementations.
Outputs unified content queue for downstream processing.
"""

import json
from pathlib import Path
from typing import List, Dict, Any

from core.events import Event
from content.generator_base import ContentGeneratorBase
from content.template_generator import TemplateContentGenerator
from content.ai_generator import AIContentGenerator


class ContentDispatcher:
    """
    Dispatches events to content generators and manages content queue.
    
    Uses dependency injection - works with any ContentGeneratorBase implementation.
    Generator is selected via config (content_mode: template | ai).
    """
    
    def __init__(self, data_dir: str = None, generator: ContentGeneratorBase = None):
        """
        Initialize the content dispatcher.
        
        Args:
            data_dir: Path to data directory (default: ../data relative to project root)
            generator: Content generator instance (optional, uses config if None)
        """
        if data_dir is None:
            # Get the data directory relative to the project
            project_root = Path(__file__).parent.parent
            self.data_dir = project_root / "data"
        else:
            self.data_dir = Path(data_dir)
        
        self.content_queue_file = self.data_dir / "content_queue.json"
        self.content_queue = []
        
        # If no generator provided, create from config
        if generator is None:
            self.generator = self._create_generator_from_config()
        else:
            self.generator = generator
    
    def _create_generator_from_config(self) -> ContentGeneratorBase:
        """
        Create content generator based on config file.
        
        Returns:
            ContentGeneratorBase implementation
        """
        config_file = self.data_dir.parent / "config" / "content_config.json"
        
        # Default to template mode
        content_mode = "template"
        
        # Try to load config
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    content_mode = config.get("content_mode", "template")
            except (json.JSONDecodeError, KeyError):
                # If config is invalid, use default
                pass
        
        # Create generator based on mode
        if content_mode == "ai":
            return AIContentGenerator()
        elif content_mode == "template":
            return TemplateContentGenerator()
        else:
            # Unknown mode, default to template
            return TemplateContentGenerator()
    
    def dispatch_events(self, events: List[Event]) -> List[Dict[str, Any]]:
        """
        Process a list of events and generate content for all platforms.
        
        Args:
            events: List of Event objects from simulation
            
        Returns:
            List of content items generated
        """
        new_content = []
        
        for event in events:
            # Generate content for each platform
            content_items = self._generate_all_content(event)
            new_content.extend(content_items)
        
        return new_content
    
    def _generate_all_content(self, event: Event) -> List[Dict[str, Any]]:
        """
        Generate content for all platforms from a single event.
        
        Uses the configured generator (template or AI).
        
        Args:
            event: Event object
            
        Returns:
            List of content dictionaries for all platforms
        """
        content_items = []
        
        # Generate ChronoNet news content
        news_content = self.generator.generate_news_content(event)
        content_items.append({
            "event_id": event.id,
            "event_type": event.type,
            "event_date": event.date.strftime('%Y-%m-%d'),
            "platform": "ChronoNet",
            "content_type": "news",
            "content": news_content
        })
        
        # Generate MindLink social content
        social_content = self.generator.generate_social_content(event)
        content_items.append({
            "event_id": event.id,
            "event_type": event.type,
            "event_date": event.date.strftime('%Y-%m-%d'),
            "platform": "MindLink",
            "content_type": "social_post",
            "content": social_content
        })
        
        # Generate NeoFlix video content
        video_content = self.generator.generate_video_content(event)
        content_items.append({
            "event_id": event.id,
            "event_type": event.type,
            "event_date": event.date.strftime('%Y-%m-%d'),
            "platform": "NeoFlix",
            "content_type": "video_intro",
            "content": video_content
        })
        
        # Generate Stellar Exchange market alert
        market_content = self.generator.generate_market_alert(event)
        content_items.append({
            "event_id": event.id,
            "event_type": event.type,
            "event_date": event.date.strftime('%Y-%m-%d'),
            "platform": "StellarExchange",
            "content_type": "market_alert",
            "content": market_content
        })
        
        return content_items
    
    def save_content_queue(self, new_content: List[Dict[str, Any]] = None):
        """
        Save content queue to JSON file.
        
        Args:
            new_content: Optional new content items to add to queue
        """
        if new_content:
            self.content_queue.extend(new_content)
        
        # Save to file with pretty formatting
        with open(self.content_queue_file, 'w', encoding='utf-8') as f:
            json.dump(self.content_queue, f, indent=2, ensure_ascii=False)
    
    def load_content_queue(self):
        """Load existing content queue from file."""
        if self.content_queue_file.exists():
            with open(self.content_queue_file, 'r', encoding='utf-8') as f:
                self.content_queue = json.load(f)
        else:
            self.content_queue = []
    
    def process_and_save(self, events: List[Event]):
        """
        Process events and save to content queue in one operation.
        
        Args:
            events: List of Event objects to process
        """
        if not events:
            return
        
        # Load existing queue
        self.load_content_queue()
        
        # Generate new content
        new_content = self.dispatch_events(events)
        
        # Save updated queue
        self.save_content_queue(new_content)
        
        return new_content
