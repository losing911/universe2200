"""
Social Media Generator for Universe 2200

Generates simulated social media feed with citizen reactions, faction propaganda,
and emergent narratives. Deterministic based on seed.
"""

import random
import math
from typing import Dict, List, Any, Optional

class SocialMediaGenerator:
    """
    Generates a feed of social media posts reacting to the world state.
    """
    
    def __init__(self, llm_client=None):
        self.factions = ["Corporate", "Civic", "Shadow", "State"]
        self.llm_client = llm_client
        
    def generate_feed(self, 
                     world_metrics: Dict[str, float],
                     latest_news: List[Dict],
                     seed: int,
                     count_range: tuple = (5, 15)) -> Dict[str, List[Dict]]:
        """
        Generate a list of social media posts.
        
        Args:
            world_metrics: Current world state metrics
            latest_news: List of recent news articles
            seed: Random seed for determinism
            count_range: Min and max number of posts to generate
            
        Returns:
            Dictionary containing list of post objects
        """
        rng = random.Random(seed)
        
        # Determine number of posts
        num_posts = rng.randint(*count_range)
        posts = []
        
        # Extract metrics
        unrest = world_metrics.get('public_unrest', 0.5)
        trust = world_metrics.get('media_trust', 0.5)
        surveillance = world_metrics.get('surveillance_level', 0.5)
        noise = world_metrics.get('information_noise', 0.5)
        
        # Analyze context from news
        news_context = self._analyze_news_context(latest_news)
        
        # AI Generation Attempt
        if self.llm_client and rng.random() < 0.3:  # 30% chance to use AI
             try:
                 ai_posts = self._generate_ai_posts(num_posts, world_metrics, news_context, seed)
                 if ai_posts:
                     return {"posts": ai_posts}
             except Exception as e:
                 print(f"AI Social Gen failed: {e}")
        
        for i in range(num_posts):
            # Deterministic post seed
            post_seed = seed + i * 7919
            post_rng = random.Random(post_seed)
            
            # Determine author type and tone based on metrics
            author_type = self._select_author_type(unrest, corp_power=world_metrics.get('corp_power_index', 0.5), rng=post_rng)
            tone = self._select_tone(author_type, unrest, trust, post_rng)
            
            # Generate content
            content = self._generate_content(author_type, tone, news_context, world_metrics, post_rng)
            
            # Calculate metadata
            sentiment = self._calculate_sentiment(tone, author_type, rng=post_rng)
            engagement = self._calculate_engagement(author_type, tone, unrest, noise, rng=post_rng)
            
            posts.append({
                "id": f"soc_{seed}_{i}",
                "author_type": author_type,
                "tone": tone,
                "content": content,
                "sentiment": round(sentiment, 2),
                "engagement": engagement,
                "timestamp": f"Tick+{i*2}m" # Simulated relative time
            })
            
        return {"posts": posts}

    def _generate_ai_posts(self, count, metrics, context, seed):
        """Generate a batch of social posts using LLM."""
        system_prompt = (
            "You are a social media simulator for a cyberpunk dystopia. "
            "Generate realistic user posts reflecting the current world state. "
            "Mix of citizens, bots, and corporate accounts. "
            "Return a JSON object with a 'posts' list."
        )
        
        user_prompt = f"""
        Generate {count} social media posts.
        Context: {context}
        Metrics: Unrest={metrics.get('public_unrest'):.2f}, Trust={metrics.get('media_trust'):.2f}
        
        Format per post:
        {{
            "author_type": "citizen|bot|faction|media",
            "tone": "string",
            "content": "string (max 280 chars)",
            "sentiment": float (-1.0 to 1.0),
            "engagement": {{ "likes": int, "reposts": int }}
        }}
        """
        
        result = self.llm_client.generate_json(system_prompt, user_prompt)
        if not result or 'posts' not in result:
            return None
            
        # Post-process to add IDs
        processed = []
        for i, p in enumerate(result['posts']):
            p['id'] = f"ai_soc_{seed}_{i}"
            p['timestamp'] = "Just now"
            processed.append(p)
            
        return processed

    def _analyze_news_context(self, news: List[Dict]) -> str:
        """Extract dominant theme from latest news."""
        if not news:
            return "general"
        
        # Simple keyword matching on titles
        text = " ".join([n.get('title', '') + " " + n.get('summary', '') for n in news]).lower()
        
        if "unrest" in text or "riot" in text or "compliance" in text:
            return "unrest"
        elif "trust" in text or "media" in text or "fake" in text:
            return "trust"
        elif "surveillance" in text or "monitoring" in text or "privacy" in text:
            return "surveillance"
        elif "corporate" in text or "market" in text or "economy" in text:
            return "corporate"
        
        return "general"

    def _select_author_type(self, unrest: float, corp_power: float, rng: random.Random) -> str:
        """Select author type based on world state."""
        # Baseline probabilities
        weights = {
            "citizen": 60,
            "faction": 20,
            "media": 10,
            "bot": 10
        }
        
        # Modifiers
        if unrest > 0.7:
            weights["citizen"] += 20  # More people complaining
            weights["bot"] += 10      # More bots trying to control narrative
            
        if corp_power > 0.7:
            weights["faction"] += 15  # More corporate propaganda
            
        # Select
        types = list(weights.keys())
        probs = [weights[t] for t in types]
        return rng.choices(types, weights=probs, k=1)[0]

    def _select_tone(self, author_type: str, unrest: float, trust: float, rng: random.Random) -> str:
        """Select tone based on author and metrics."""
        if author_type == "faction":
            return "propaganda"
        elif author_type == "media":
            return "neutral" if trust > 0.4 else "sensationalist"
        elif author_type == "bot":
            return rng.choice(["propaganda", "spam", "conspiracy"])
            
        # Citizens
        tones = ["neutral", "anxious", "angry", "conspiracy", "hopeful"]
        weights = [20, 20, 20, 20, 20]
        
        # Adjust citizen weights
        if unrest > 0.6:
            weights[1] += 30 # Anxious
            weights[2] += 40 # Angry
        if trust < 0.3:
            weights[3] += 50 # Conspiracy
            
        return rng.choices(tones, weights=weights, k=1)[0]

    def _generate_content(self, author_type: str, tone: str, context: str, 
                         metrics: Dict[str, float], rng: random.Random) -> str:
        """Generate text content using template assembly."""
        
        templates = {
            "citizen": {
                "angry": [
                    "They think we don't see what's happening. We see everything.",
                    "Another day, another restriction. when does it end?",
                    "The system isn't broken, it's working exactly as designed to crush us.",
                    "How much more can they take from us before we snap?",
                    f"Unrest is at {metrics.get('public_unrest', 0):.2f}? Feels higher on the street."
                ],
                "anxious": [
                    "Is it safe to go out tonight? Hearing sirens everywhere.",
                    "Supplies are getting low again. panic buying starting.",
                    "I just want a normal day for once.",
                    "The news says calm, but my connection keeps dropping.",
                    "Anyone else feeling like something big is about to happen?"
                ],
                "conspiracy": [
                    "The static in the feeds isn't random. It's a code.",
                    "They aren't technically 'people' anymore if you check the bios.",
                    "The outage wasn't an accident. Check the timestamp patterns.",
                    "Don't trust the official metrics. They cap the display at 0.99.",
                    "New surveillance drones aren't for safety, they're precise mapping."
                ],
                "neutral": [
                    "Just trying to get to work on time.",
                    "Weather control seems stuck on 'gloom' again.",
                    "Anyone have a spare filter cartridge? will trade.",
                    "Metro delayed again due to 'security incident'.",
                    "Coffee tastes like burnt copper today."
                ]
            },
            "faction": {
                "propaganda": [
                    "Trust the plan. Order brings prosperity.",
                    "The Corporation protects those who contribute.",
                    "Dissident activity only prolongs the suffering.",
                    "Report suspicious behavior. Earn credits. Stay safe.",
                    "Unity through compliance. Innovation through discipline."
                ]
            },
            "media": {
                "neutral": [
                    "Updates on the developing situation in Sector 4.",
                    "Market indices show slight volatility in opening trading.",
                    "Weather advisory: Acid rain expected in lower distracts.",
                    "Official statement regarding yesterday's outage.",
                    "Techno-infrastructure maintenance scheduled for tonight."
                ],
                "sensationalist": [
                    "CRISIS ALERT: Are your neighbors safe?",
                    "What they aren't telling you about the food supply!",
                    "10 signs the economy is about to crash HARD.",
                    "EXCLUSIVE: Leaked data reveals shocking truth!",
                    "PANIC in the streets? Watch live footage now!"
                ]
            },
            "bot": {
                "propaganda": [
                    "Everything is fine. #Unity #Order",
                    "Support the leadership. #Patriot",
                    "Dissent is treason. #SafetyFirst",
                ],
                "spam": [
                    "Get 500% returns on crypto-scrip! Link in bio!",
                    "Hide from drones with this one weird trick.",
                    "Clean water filters - 50% off today only!"
                ],
                "conspiracy": [
                    "WAKE UP SHEEPLE",
                    "The signals are real.",
                    "Look at the sky."
                ]
            }
        }
        
        # Fallback to citizen neutral if specific template missing
        category = templates.get(author_type, templates["citizen"])
        options = category.get(tone, category.get("neutral", ["Start processing..."]))
        
        # Context injection (simple appendix)
        base_text = rng.choice(options)
        
        context_tags = {
            "unrest": " #Unrest #Sector7",
            "trust": " #FakeNews #Truth",
            "surveillance": " #EyesEverywhere #Privacy",
            "corporate": " #CorpLife #Economy",
            "general": " #CityLife"
        }
        
        return base_text + context_tags.get(context, "")

    def _calculate_sentiment(self, tone: str, author_type: str, rng: random.Random) -> float:
        """Calculate sentiment score (-1 to 1)."""
        base_sentiments = {
            "angry": -0.8,
            "anxious": -0.6,
            "conspiracy": -0.4,
            "neutral": 0.0,
            "hopeful": 0.6,
            "propaganda": 0.5, # Positive for the regime
            "sensationalist": -0.3,
            "spam": 0.1
        }
        
        base = base_sentiments.get(tone, 0.0)
        variance = rng.uniform(-0.1, 0.1)
        return max(-1.0, min(1.0, base + variance))

    def _calculate_engagement(self, author_type: str, tone: str, unrest: float, 
                            noise: float, rng: random.Random) -> int:
        """Calculate simulated engagement (likes/shares)."""
        base = rng.randint(1, 50)
        
        # Multipliers
        mult = 1.0
        
        # High unrest fuels anger/anxiety engagement
        if unrest > 0.7 and tone in ["angry", "anxious", "sensationalist"]:
            mult *= 3.0
            
        # High noise drowns out neutral content
        if noise > 0.7 and tone == "neutral":
            mult *= 0.5
            
        # Propaganda bots get boosted or ignored depending on trust? 
        # For now, let's say they have low engagement unless swarming
        if author_type == "bot":
            mult *= 0.2
            
        # Factions buy engagement
        if author_type == "faction":
            mult *= 5.0
            
        return int(base * mult)
