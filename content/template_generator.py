"""
Template-Based Content Generator

Implements template-based content generation using predefined templates.
This is the deterministic, non-AI implementation.
"""

from typing import Dict, Any
import re

from content.generator_base import ContentGeneratorBase
from content import templates
from core.events import Event


class TemplateContentGenerator(ContentGeneratorBase):
    """
    Template-based content generator.
    
    Uses predefined templates and deterministic rules to generate content.
    No AI, no randomness - purely template-driven.
    """
    
    def __init__(self):
        """Initialize template content generator."""
        pass
    
    def generate_news_content(self, event: Event) -> Dict[str, Any]:
        """Generate news content using templates."""
        # Extract event data
        event_type = event.type
        event_type_display = templates.EVENT_TYPE_NAMES.get(event_type, event_type.title())
        location = event.location
        date = event.date.strftime('%Y-%m-%d')
        scale = event.scale
        visibility = event.visibility
        
        # Get metadata
        metadata = event.metadata
        participants = metadata.get('participants_estimated', 'Unknown')
        
        # Determine derived values
        severity_label = templates.get_severity_label(scale)
        tone = templates.get_tone(scale, visibility)
        scale_display = self._get_scale_display(scale)
        
        # Determine reliability
        if visibility >= 0.8:
            reliability = "Confirmed"
        elif visibility >= 0.5:
            reliability = "Under Verification"
        else:
            reliability = "Unconfirmed Reports"
        
        # Determine category
        if event_type in ["protest", "political_crisis"]:
            category = "Politics & Society"
        elif event_type in ["economic_shift", "resource_shortage"]:
            category = "Economy"
        elif event_type in ["corporate_action"]:
            category = "Business"
        else:
            category = "Technology & AI"
        
        # Fill template
        return {
            "headline": templates.NEWS_TEMPLATE["headline"].format(
                event_type_display=event_type_display,
                location=location
            ),
            "summary": templates.NEWS_TEMPLATE["summary"].format(
                date=date,
                event_type=event_type,
                location=location,
                scale_display=scale_display
            ),
            "details": {
                "event_type": event_type,
                "location": location,
                "date": date,
                "scale": round(scale, 2),
                "visibility": round(visibility, 2),
                "participants": participants,
                "severity": severity_label
            },
            "tone": tone,
            "reliability": reliability,
            "category": category
        }
    
    def generate_social_content(self, event: Event) -> Dict[str, Any]:
        """Generate social media content using templates."""
        event_type = event.type
        event_type_display = templates.EVENT_TYPE_NAMES.get(event_type, event_type.title())
        location = event.location
        date = event.date.strftime('%Y-%m-%d')
        scale = event.scale
        visibility = event.visibility
        
        # Get emoji and scale bar
        emoji = templates.get_event_emoji(event_type)
        scale_bar = templates.get_scale_bar(scale)
        
        # Determine urgency
        if scale >= 0.7:
            urgency_level = "HIGH"
        elif scale >= 0.4:
            urgency_level = "MEDIUM"
        else:
            urgency_level = "LOW"
        
        # Engagement priority
        if visibility >= 0.7:
            engagement_priority = "BOOST"
        elif visibility >= 0.5:
            engagement_priority = "NORMAL"
        else:
            engagement_priority = "LOW"
        
        return {
            "text": f"{emoji} {event_type_display} in {location} | Scale: {scale_bar} | {date}",
            "hashtags": [
                f"#{self._sanitize_location(location)}",
                f"#{event_type}",
                "#2200Evreni"
            ],
            "urgency": urgency_level,
            "visibility_level": round(visibility, 2),
            "engagement_priority": engagement_priority
        }
    
    def generate_video_content(self, event: Event) -> Dict[str, Any]:
        """Generate video content using templates."""
        event_type = event.type
        event_type_display = templates.EVENT_TYPE_NAMES.get(event_type, event_type.title())
        location = event.location
        date = event.date.strftime('%Y-%m-%d')
        scale = event.scale
        
        severity_label = templates.get_severity_label(scale)
        scale_display = self._get_scale_display(scale)
        context = self._get_context_note(event_type, scale)
        duration = self._get_estimated_duration(scale)
        
        # Production priority
        if scale >= 0.7:
            production_priority = "URGENT"
        elif scale >= 0.5:
            production_priority = "HIGH"
        else:
            production_priority = "STANDARD"
        
        return {
            "title": f"{event_type_display} at {location} - {date}",
            "description": f"Breaking coverage of {event_type} event at {location}. Magnitude: {scale_display}. {context}",
            "thumbnail_suggestion": f"{location} | {event_type_display} | {severity_label}",
            "tags": [event_type, location, "2207", "universe_chronicle"],
            "duration_estimate": duration,
            "production_priority": production_priority
        }
    
    def generate_market_alert(self, event: Event) -> Dict[str, Any]:
        """Generate market alert using templates."""
        event_type = event.type
        event_type_display = templates.EVENT_TYPE_NAMES.get(event_type, event_type.title())
        location = event.location
        date = event.date.strftime('%Y-%m-%d')
        scale = event.scale
        
        severity_label = templates.get_severity_label(scale)
        affected_sectors = templates.get_affected_sectors(event_type, scale)
        estimated_impact = templates.get_market_impact(event_type, scale)
        
        # Alert type
        if "crisis" in event_type or scale >= 0.7:
            alert_type = "RISK_ALERT"
        elif scale >= 0.5:
            alert_type = "WATCH"
        else:
            alert_type = "INFO"
        
        # Recommendation
        if scale >= 0.8:
            recommendation = "Monitor positions closely"
        elif scale >= 0.6:
            recommendation = "Review exposure to affected sectors"
        elif scale >= 0.4:
            recommendation = "Stay informed"
        else:
            recommendation = "No action required"
        
        return {
            "alert_type": alert_type,
            "affected_sectors": affected_sectors,
            "severity": severity_label,
            "message": f"Market Alert: {event_type_display} event may impact {affected_sectors}",
            "timestamp": date,
            "location_affected": location,
            "estimated_impact": estimated_impact,
            "recommendation": recommendation
        }
    
    # Helper methods
    
    @staticmethod
    def _sanitize_location(location: str) -> str:
        """Sanitize location for hashtags."""
        return re.sub(r'[^a-zA-Z0-9]', '', location)
    
    @staticmethod
    def _get_scale_display(scale: float) -> str:
        """Convert scale to descriptive text."""
        if scale >= 0.8:
            return "massive scale"
        elif scale >= 0.6:
            return "large scale"
        elif scale >= 0.4:
            return "moderate scale"
        elif scale >= 0.2:
            return "small scale"
        else:
            return "minor scale"
    
    @staticmethod
    def _get_estimated_duration(scale: float) -> str:
        """Estimate video duration."""
        if scale >= 0.8:
            return "10-15 min"
        elif scale >= 0.6:
            return "7-10 min"
        elif scale >= 0.4:
            return "5-7 min"
        else:
            return "3-5 min"
    
    @staticmethod
    def _get_context_note(event_type: str, scale: float) -> str:
        """Generate context note for video."""
        context_map = {
            "protest": "Citizens mobilize in response to growing concerns.",
            "political_crisis": "Authorities face mounting pressure as situation develops.",
            "economic_shift": "Market conditions show significant changes.",
            "resource_shortage": "Supply concerns affect local population.",
            "corporate_action": "Major corporate movement detected.",
            "media_incident": "Information reliability under scrutiny.",
            "ai_incident": "AI systems exhibit unexpected behavior."
        }
        return context_map.get(event_type, "Situation developing.")
