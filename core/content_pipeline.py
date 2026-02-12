"""
Content Pipeline for Universe 2200

Detects significant events from world state and generates structured content.
Runs after each simulation tick to produce news, social posts, and trending topics.

This is a read-only observer that does NOT mutate world state.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from core.tick_context import TickContext
from content.news_generator import generate_news
from content.social_media_generator import SocialMediaGenerator

logger = logging.getLogger("ContentPipeline")


class ContentPipeline:
    """
    Content generation pipeline for broadcast-style content.
    
    Detects significant world events and generates:
    - News articles
    - Social media posts
    - Trending topics
    - Metric summaries
    
    Stateless and deterministic based on world state + tick context.
    """
    
    # Event detection thresholds
    THRESHOLDS = {
        "unrest_spike": 0.8,      # High unrest
        "unrest_critical": 0.95,   # Critical unrest
        "trust_collapse": 0.2,     # Low media trust
        "trust_lost": 0.05,        # Almost no trust
        "noise_high": 0.8,         # High information noise
        "surveillance_high": 0.8,  # Heavy surveillance
        "corporate_power": 0.8,    # Corporate dominance
    }
    
    def __init__(self):
        """Initialize content pipeline."""
        self.social_gen = SocialMediaGenerator()
    
    def run(self, 
            tick_context: TickContext,
            world_state,
            recent_posts: List[Dict] = None) -> Dict[str, Any]:
        """
        Generate content based on current world state.
        
        Args:
            tick_context: Current tick context (for determinism)
            world_state: WorldState instance (read-only)
            recent_posts: Optional list of recent social posts for context
            
        Returns:
            Structured content output as dictionary
        """
        logger.debug(f"Running ContentPipeline for tick {tick_context.tick_number}")
        
        # Read world state (no mutation)
        metrics = self._extract_metrics(world_state)
        
        # Detect significant events
        events = self._detect_events(metrics, tick_context)
        
        # Generate content based on events
        news_articles = self._generate_news(events, metrics, tick_context)
        social_posts = self._generate_social_posts(events, metrics, tick_context, news_items=news_articles)
        trending_topics = self._generate_trending_topics(events, metrics)
        
        # Generate headline
        headline = self._generate_headline(events, metrics)
        
        # Assemble output
        output = {
            "tick": tick_context.tick_number,
            "timestamp": tick_context.timestamp.isoformat(),
            "headline": headline,
            "news": news_articles,
            "social_feed": social_posts,
            "trending": trending_topics,
            "metrics": metrics,
            "events_detected": [e["type"] for e in events]
        }
        
        logger.info(f"Generated content: {len(news_articles)} news, "
                   f"{len(social_posts)} posts, {len(trending_topics)} trending")
        
        return output
    
    def _extract_metrics(self, world_state) -> Dict[str, float]:
        """Extract current metrics from world state."""
        return {
            "public_unrest": world_state.public_unrest,
            "media_trust": world_state.media_trust,
            "information_noise": world_state.information_noise,
            "surveillance_level": world_state.surveillance_level,
            "ai_dependency": getattr(world_state, 'ai_dependency', 0.5),
            "corp_power_index": getattr(world_state, 'corp_power_index', 0.5),
            "market_confidence": getattr(world_state, 'market_confidence', 0.5),
        }
    
    def _detect_events(self, metrics: Dict[str, float], tick_context: TickContext) -> List[Dict]:
        """
        Detect significant events based on metrics.
        
        Returns list of event dictionaries with type and severity.
        """
        events = []
        
        # Unrest events
        if metrics["public_unrest"] >= self.THRESHOLDS["unrest_critical"]:
            events.append({
                "type": "unrest_critical",
                "severity": "critical",
                "value": metrics["public_unrest"]
            })
        elif metrics["public_unrest"] >= self.THRESHOLDS["unrest_spike"]:
            events.append({
                "type": "unrest_spike",
                "severity": "high",
                "value": metrics["public_unrest"]
            })
        
        # Trust events
        if metrics["media_trust"] <= self.THRESHOLDS["trust_lost"]:
            events.append({
                "type": "trust_lost",
                "severity": "critical",
                "value": metrics["media_trust"]
            })
        elif metrics["media_trust"] <= self.THRESHOLDS["trust_collapse"]:
            events.append({
                "type": "trust_collapse",
                "severity": "high",
                "value": metrics["media_trust"]
            })
        
        # Information noise
        if metrics["information_noise"] >= self.THRESHOLDS["noise_high"]:
            events.append({
                "type": "information_chaos",
                "severity": "high",
                "value": metrics["information_noise"]
            })
        
        # Surveillance state
        if metrics["surveillance_level"] >= self.THRESHOLDS["surveillance_high"]:
            events.append({
                "type": "surveillance_state",
                "severity": "high",
                "value": metrics["surveillance_level"]
            })
        
        # Corporate takeover
        if metrics["corp_power_index"] >= self.THRESHOLDS["corporate_power"]:
            events.append({
                "type": "corporate_dominance",
                "severity": "high",
                "value": metrics["corp_power_index"]
            })
        
        # Combined crisis (multiple high-severity events)
        if len([e for e in events if e["severity"] == "critical"]) >= 2:
            events.append({
                "type": "systemic_crisis",
                "severity": "critical",
                "value": 1.0
            })
        
        return events
    
    def _generate_headline(self, events: List[Dict], metrics: Dict[str, float]) -> str:
        """Generate main headline based on most severe event."""
        if not events:
            return "Universe 2200: Stability Maintained"
        
        # Sort by severity
        critical_events = [e for e in events if e["severity"] == "critical"]
        if critical_events:
            primary = critical_events[0]
        else:
            primary = events[0]
        
        # Generate headline based on event type
        headlines = {
            "unrest_critical": "BREAKING: Civil Unrest Reaches Critical Levels",
            "unrest_spike": "Public Unrest Escalates Across Sectors",
            "trust_lost": "Media Trust Collapses - Information Crisis Declared",
            "trust_collapse": "Declining Media Trust Threatens Social Cohesion",
            "information_chaos": "Information Overload: Citizens Struggle to Discern Truth",
            "surveillance_state": "Surveillance Reaches Unprecedented Levels",
            "corporate_dominance": "Corporate Influence Reshapes Governance",
            "systemic_crisis": "ALERT: Multiple Systems in Critical Failure State",
        }
        
        return headlines.get(primary["type"], "Universe 2200: Significant Developments")
    
    def _generate_news(self, events: List[Dict], metrics: Dict[str, float], 
                       tick_context: TickContext) -> List[Dict]:
        """Generate news articles based on detected events."""
        news = []
        
        for event in events:
            article = self._create_news_article(event, metrics, tick_context)
            if article:
                news.append(article)
        
        # Always include a metrics summary article
        news.append({
            "id": f"news_metrics_{tick_context.tick_number}",
            "type": "metrics_summary",
            "title": "Daily Metrics Report",
            "summary": f"Unrest: {metrics['public_unrest']:.2f}, "
                      f"Trust: {metrics['media_trust']:.2f}, "
                      f"Noise: {metrics['information_noise']:.2f}",
            "content": self._format_metrics_report(metrics),
            "timestamp": tick_context.timestamp.isoformat()
        })
        
        return news
    
    def _create_news_article(self, event: Dict, metrics: Dict[str, float],
                            tick_context: TickContext) -> Optional[Dict]:
        """Create a news article for a specific event."""
        
        # Use deterministic seed for this specific news item
        # Combine tick seed with event hash to ensure uniqueness per event
        news_seed = tick_context.tick_seed + hash(event['type'])
        
        # Generator expects metrics dict
        article_data = generate_news(event, metrics, news_seed)
        
        return {
            "id": f"news_{event['type']}_{tick_context.tick_number}",
            "type": event["type"],
            "severity": event["severity"],
            "title": article_data["headline"],
            "summary": article_data["summary"],
            "content": article_data["summary"], # For now content is same as summary, can be expanded
            "bias_score": article_data["bias_score"],
            "impact_level": article_data["impact_level"],
            "timestamp": tick_context.timestamp.isoformat()
        }
    
    def _generate_social_posts(self, events: List[Dict], metrics: Dict[str, float],
                               tick_context: TickContext, news_items: List[Dict] = None) -> List[Dict]:
        """Generate social media posts reflecting public sentiment."""
        
        # Use deterministic seed for social feed
        feed_seed = tick_context.tick_seed + 999
        
        # Generate feed using SocialMediaGenerator
        # It handles tone, content, and engagement based on metrics/news
        feed_data = self.social_gen.generate_feed(
            world_metrics=metrics,
            latest_news=news_items or [],
            seed=feed_seed,
            count_range=(5, 10)
        )
        
        return feed_data["posts"]
    
    def _create_social_post(self, event: Dict, metrics: Dict[str, float],
                           tick_context: TickContext) -> Optional[Dict]:
        """Create a social post for a specific event."""
        
        # Generate deterministic user ID based on tick and event
        user_id = f"observer_{(tick_context.tick_number * 13 + hash(event['type'])) % 1000:04d}"
        
        post_templates = {
            "unrest_critical": [
                "This is getting out of hand. Something has to change. #Unrest",
                "We can't keep living like this. The system is broken. #Crisis",
            ],
            "trust_collapse": [
                "Can't trust anything we read anymore. Where's the truth? #MediaCrisis",
                "Information sources are completely compromised. #TrustNoOne",
            ],
            "surveillance_state": [
                "Cameras everywhere. Privacy is a memory. #Surveillance",
                "They're watching everything we do now. #1984",
            ],
            "corporate_dominance": [
                "Corporations run everything. We're just consumers. #CorporateState",
                "Public interest? More like profit margins. #CapitalismUnbound",
            ]
        }
        
        templates = post_templates.get(event["type"])
        if not templates:
            return None
        
        # Select template deterministically
        template_idx = tick_context.tick_number % len(templates)
        content = templates[template_idx]
        
        return {
            "id": f"post_{event['type']}_{tick_context.tick_number}",
            "user_id": user_id,
            "content": content,
            "type": "reaction",
            "event_type": event["type"],
            "timestamp": tick_context.timestamp.isoformat()
        }
    
    def _generate_trending_topics(self, events: List[Dict], 
                                  metrics: Dict[str, float]) -> List[Dict]:
        """Generate trending topics based on current events."""
        trending = []
        
        # Event-based trending topics
        topic_map = {
            "unrest_critical": {"tag": "#Unrest", "volume": "high"},
            "unrest_spike": {"tag": "#PublicProtest", "volume": "rising"},
            "trust_collapse": {"tag": "#MediaCrisis", "volume": "high"},
            "trust_lost": {"tag": "#TrustNoOne", "volume": "critical"},
            "surveillance_state": {"tag": "#Surveillance", "volume": "high"},
            "corporate_dominance": {"tag": "#CorporateState", "volume": "rising"},
            "information_chaos": {"tag": "#InfoOverload", "volume": "high"},
        }
        
        for event in events:
            topic = topic_map.get(event["type"])
            if topic:
                trending.append({
                    "tag": topic["tag"],
                    "volume": topic["volume"],
                    "related_event": event["type"]
                })
        
        # Always include current state topics
        if metrics["public_unrest"] > 0.5:
            trending.append({"tag": "#CurrentState", "volume": "steady"})
        
        return trending[:5]  # Top 5 trending
    
    def _format_metrics_report(self, metrics: Dict[str, float]) -> str:
        """Format metrics into a readable report."""
        return (
            f"Public Unrest: {metrics['public_unrest']:.3f}\n"
            f"Media Trust: {metrics['media_trust']:.3f}\n"
            f"Information Noise: {metrics['information_noise']:.3f}\n"
            f"Surveillance Level: {metrics['surveillance_level']:.3f}\n"
            f"AI Dependency: {metrics['ai_dependency']:.3f}\n"
            f"Corporate Power: {metrics['corp_power_index']:.3f}\n"
            f"Market Confidence: {metrics['market_confidence']:.3f}"
        )
