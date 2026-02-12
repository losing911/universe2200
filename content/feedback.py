"""
Content Feedback Analyzer Module

Analyzes generated content and applies feedback effects to world state.
This creates a complete feedback loop: Events → Content → World State → Events
"""

import json
from pathlib import Path
from typing import Dict, Any, List

from core.state import WorldState


class FeedbackAnalyzer:
    """
    Analyzes content and applies feedback effects to world state.
    Creates a circular feedback system where media coverage influences reality.
    """
    
    def __init__(self, config_path: str = None, enabled: bool = True):
        """
        Initialize the feedback analyzer.
        
        Args:
            config_path: Path to feedback_weights.json (optional)
            enabled: Whether feedback is enabled (can be toggled)
        """
        self.enabled = enabled
        
        if config_path is None:
            project_root = Path(__file__).parent.parent
            config_path = project_root / "config" / "feedback_weights.json"
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load feedback configuration from JSON file."""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            # Default config if file doesn't exist
            return {
                "enabled": True,
                "platform_weights": {
                    "ChronoNet": {"public_awareness": 0.05},
                    "MindLink": {"public_sentiment_positive": 0.03, "public_sentiment_negative": -0.04},
                    "NeoFlix": {"amplification_multiplier": 1.5},
                    "StellarExchange": {"market_confidence": -0.02}
                }
            }
    
    def analyze_content(self, content_items: List[Dict[str, Any]], current_state: WorldState) -> Dict[str, float]:
        """
        Analyze content and calculate aggregate effects.
        
        Args:
            content_items: List of content items from content_queue.json
            current_state: Current world state (to check current values)
            
        Returns:
            Dictionary of metric changes to apply
        """
        if not self.enabled or not self.config.get("enabled", True):
            return {}
        
        # Aggregate effects
        effects = {
            'public_awareness': 0.0,
            'public_sentiment': 0.0,
            'market_confidence': 0.0
        }
        
        # Group content by date to process daily
        by_date = {}
        for item in content_items:
            date = item.get('event_date', 'unknown')
            if date not in by_date:
                by_date[date] = []
            by_date[date].append(item)
        
        # Process each day's content
        for date, items in by_date.items():
            day_effects = self._analyze_day(items)
            
            # Accumulate effects
            for metric, delta in day_effects.items():
                effects[metric] = effects.get(metric, 0) + delta
        
        # Apply daily decay
        if 'daily_decay' in self.config:
            decay = self.config['daily_decay']
            
            if 'public_awareness' in decay:
                effects['public_awareness'] += decay['public_awareness']
            
            # Sentiment moves toward neutral
            if 'public_sentiment' in decay:
                sentiment_decay = decay['public_sentiment'].get('toward_neutral', 0)
                current_sentiment = current_state.public_sentiment
                
                if current_sentiment > 0.5:
                    effects['public_sentiment'] -= sentiment_decay
                elif current_sentiment < 0.5:
                    effects['public_sentiment'] += sentiment_decay
        
        return effects
    
    def _analyze_day(self, content_items: List[Dict[str, Any]]) -> Dict[str, float]:
        """Analyze content for a single day."""
        effects = {
            'public_awareness': 0.0,
            'public_sentiment': 0.0,
            'market_confidence': 0.0
        }
        
        amplification = 1.0
        
        for item in content_items:
            platform = item.get('platform')
            content = item.get('content', {})
            
            if platform == 'ChronoNet':
                # News increases public awareness
                weight = self.config['platform_weights']['ChronoNet']['public_awareness']
                effects['public_awareness'] += weight
            
            elif platform == 'MindLink':
                # Social media affects sentiment
                sentiment_effect = self._determine_sentiment(content)
                effects['public_sentiment'] += sentiment_effect
            
            elif platform == 'NeoFlix':
                # Video amplifies impact
                production_priority = content.get('production_priority', 'STANDARD')
                amp_config = self.config.get('amplification_thresholds', {}).get('NeoFlix', {})
                amplification = max(amplification, amp_config.get(production_priority, 1.0))
            
            elif platform == 'StellarExchange':
                # Market alerts affect confidence
                weight = self.config['platform_weights']['StellarExchange']['market_confidence']
                
                # More severe alerts have stronger effect
                severity = content.get('severity', 'MEDIUM')
                severity_multiplier = {
                    'CRITICAL': 2.0,
                    'HIGH': 1.5,
                    'MEDIUM': 1.0,
                    'LOW': 0.5,
                    'MINIMAL': 0.2
                }.get(severity, 1.0)
                
                effects['market_confidence'] += weight * severity_multiplier
        
        # Apply amplification from video content
        if amplification > 1.0:
            for metric in effects:
                effects[metric] *= amplification
        
        return effects
    
    def _determine_sentiment(self, content: Dict[str, Any]) -> float:
        """Determine sentiment impact from social media content."""
        weights = self.config['platform_weights']['MindLink']
        
        # Check tone and urgency to determine positive/negative
        tone = content.get('tone', 'neutral')
        urgency = content.get('urgency', 'LOW')
        
        # Negative sentiment if urgent/serious
        if urgency in ['HIGH', 'CRITICAL'] or tone in ['urgent', 'serious']:
            return weights['public_sentiment_negative']
        
        # Positive sentiment if informative/low urgency
        elif urgency == 'LOW' or tone == 'informative':
            return weights['public_sentiment_positive']
        
        # Neutral
        return 0.0
    
    def apply_feedback(self, content_items: List[Dict[str, Any]], world_state: WorldState) -> Dict[str, float]:
        """
        Analyze content and apply feedback to world state.
        
        Args:
            content_items: List of content to analyze
            world_state: WorldState to apply effects to
            
        Returns:
            Dictionary of effects that were applied
        """
        if not content_items:
            return {}
        
        # Calculate aggregate effects
        effects = self.analyze_content(content_items, world_state)
        
        if not effects:
            return {}
        
        # Apply effects using the traceable apply_effect method
        world_state.apply_effect("content_feedback", effects)
        
        return effects
