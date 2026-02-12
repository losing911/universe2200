"""
Content Templates Module

Defines pure templates for transforming simulation events into platform-specific content.
No creative generation - just structured placeholders for deterministic output.
"""

from typing import Dict, Any


# ChronoNet News Template - Structured news content
NEWS_TEMPLATE = {
    "headline": "⚠️ {event_type_display} reported in {location}",
    "summary": "On {date}, an event classified as {event_type} occurred at {location} with a magnitude of {scale_display}.",
    "details": {
        "event_type": "{event_type}",
        "location": "{location}",
        "date": "{date}",
        "scale": "{scale}",
        "visibility": "{visibility}",
        "participants": "{participants}",
        "severity": "{severity_label}"
    },
    "tone": "{tone}",
    "reliability": "{reliability}",
    "category": "{category}"
}


# MindLink Social Post Template - Concise social media style
SOCIAL_TEMPLATE = {
    "text": "{emoji} {event_type_display} in {location} | Scale: {scale_bar} | {date}",
    "hashtags": ["#{sanitized_location}", "#{event_type}", "#2200Evreni"],
    "urgency": "{urgency_level}",
    "visibility_level": "{visibility}",
    "engagement_priority": "{engagement_priority}"
}


# NeoFlix Video Intro Template - Video description structure
VIDEO_TEMPLATE = {
    "title": "{event_type_display} at {location} - {date}",
    "description": "Breaking coverage of {event_type} event at {location}. Magnitude: {scale_display}. {context_note}",
    "thumbnail_suggestion": "{location} | {event_type} | {severity_label}",
    "tags": ["{event_type}", "{location}", "2207", "universe_chronicle"],
    "duration_estimate": "{estimated_duration}",
    "production_priority": "{production_priority}"
}


# Stellar Exchange Market Alert Template - Economic impact signal
MARKET_ALERT_TEMPLATE = {
    "alert_type": "{alert_type}",
    "affected_sectors": "{affected_sectors}",
    "severity": "{severity_label}",
    "message": "Market Alert: {event_type_display} event may impact {affected_sectors}",
    "timestamp": "{date}",
    "location_affected": "{location}",
    "estimated_impact": "{estimated_impact}",
    "recommendation": "{recommendation}"
}


# Template mapping for easy lookup
TEMPLATES = {
    "news": NEWS_TEMPLATE,
    "social": SOCIAL_TEMPLATE,
    "video": VIDEO_TEMPLATE,
    "market_alert": MARKET_ALERT_TEMPLATE
}


# Event type display names (human-readable)
EVENT_TYPE_NAMES = {
    "protest": "Protest",
    "political_crisis": "Political Crisis",
    "economic_shift": "Economic Shift",
    "corporate_action": "Corporate Action",
    "media_incident": "Media Incident",
    "ai_incident": "AI Incident",
    "resource_shortage": "Resource Shortage"
}


# Severity labels based on scale
def get_severity_label(scale: float) -> str:
    """Determine severity label based on event scale."""
    if scale >= 0.8:
        return "CRITICAL"
    elif scale >= 0.6:
        return "HIGH"
    elif scale >= 0.4:
        return "MEDIUM"
    elif scale >= 0.2:
        return "LOW"
    else:
        return "MINIMAL"


# Scale visualization bar
def get_scale_bar(scale: float) -> str:
    """Create a visual scale indicator."""
    filled = int(scale * 10)
    return "█" * filled + "░" * (10 - filled)


# Emoji mapping for social posts
def get_event_emoji(event_type: str) -> str:
    """Get emoji for event type."""
    emoji_map = {
        "protest": "📢",
        "political_crisis": "🚨",
        "economic_shift": "📈",
        "corporate_action": "🏢",
        "media_incident": "📰",
        "ai_incident": "🤖",
        "resource_shortage": "⚠️"
    }
    return emoji_map.get(event_type, "📌")


# Tone determination based on visibility and scale
def get_tone(scale: float, visibility: float) -> str:
    """Determine content tone based on event metrics."""
    if scale >= 0.7 and visibility >= 0.7:
        return "urgent"
    elif scale >= 0.5:
        return "serious"
    elif visibility >= 0.6:
        return "alert"
    else:
        return "informative"


# Market sectors affected by event type
def get_affected_sectors(event_type: str, scale: float) -> str:
    """Determine which market sectors are affected."""
    sector_map = {
        "protest": "Public Services, Security",
        "political_crisis": "Government Bonds, Infrastructure",
        "economic_shift": "General Markets",
        "corporate_action": "Corporate Equities",
        "media_incident": "Media Stocks, Communications",
        "ai_incident": "Technology, AI Systems",
        "resource_shortage": "Commodities, Utilities"
    }
    return sector_map.get(event_type, "General Markets")


# Market impact estimation
def get_market_impact(event_type: str, scale: float) -> str:
    """Estimate market impact level."""
    if scale >= 0.8:
        return "High Volatility Expected"
    elif scale >= 0.6:
        return "Moderate Impact Likely"
    elif scale >= 0.4:
        return "Minor Fluctuations Possible"
    else:
        return "Minimal Market Effect"
