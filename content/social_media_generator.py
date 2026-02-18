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
                     platform: str = "x", # 'x' or 'insta'
                     count_range: tuple = (5, 15)) -> Dict[str, List[Dict]]:
        """
        Generate a list of social media posts for a specific platform.
        """
        rng = random.Random(seed)
        
        # Determine number of posts
        num_posts = rng.randint(*count_range)
        posts = []
        
        # Extract metrics
        unrest = world_metrics.get('public_unrest', 0.5)
        trust = world_metrics.get('media_trust', 0.5)
        noise = world_metrics.get('information_noise', 0.5)
        
        # Analyze context from news
        news_context = self._analyze_news_context(latest_news)
        
        # [NEW] Try AI Generation first
        if self.llm_client and rng.random() < 0.8: # 80% chance for AI if available
            try:
                ai_posts_data = self._generate_ai_posts(num_posts, world_metrics, news_context, list(post_rng.getstate()))
                if ai_posts_data:
                    return {"posts": ai_posts_data}
            except Exception as e:
                print(f"AI Social Gen failed (fallback to properties): {e}")

        # Fallback / Deterministic Loop
        
        for i in range(num_posts):
            # Deterministic post seed
            post_seed = seed + i * 7919
            post_rng = random.Random(post_seed)
            
            # Select Author Type based on Platform & Metrics
            author_type = self._select_author_type(unrest, platform, post_rng)
            
            # Generate ID
            post_id = f"{platform}_{seed}_{i}"
            
            # Generate Platform Specific Content
            if platform == "x":
                content_data = self._generate_x_content(author_type, news_context, world_metrics, post_rng)
            else:
                content_data = self._generate_insta_content(author_type, news_context, world_metrics, post_rng)
                
            # Calculate Engagement
            engagement = self._calculate_engagement(author_type, "neutral", unrest, noise, rng=post_rng)
            
            post = {
                "id": post_id,
                "platform": platform,
                "author_type": author_type,
                "timestamp": f"Tick+{i*2}m",
                "engagement": engagement,
                **content_data
            }
            posts.append(post)
            
        return {"posts": posts}

    def _select_author_type(self, unrest: float, platform: str, rng: random.Random) -> str:
        """Select author type based on world state and platform."""
        # Baseline probabilities
        weights = {
            "citizen": 50,
            "influencer": 5,
            "faction": 15,
            "media": 10,
            "bot": 10,
            "troll": 5,
            "comedian": 5
        }
        
        # Platform adjustments
        if platform == "insta":
            weights["influencer"] += 20
            weights["citizen"] += 10
            weights["faction"] -= 10
            weights["troll"] -= 5 # Less trolling on insta? debatable
            
        if platform == "x":
            weights["troll"] += 10
            weights["bot"] += 10
            weights["media"] += 10
            
        # World State Adjustments
        if unrest > 0.7:
            weights["citizen"] += 10
            weights["bot"] += 10
            
        types = list(weights.keys())
        probs = [weights[t] for t in types]
        return rng.choices(types, weights=probs, k=1)[0]

    def _generate_x_content(self, author_type: str, context: str, metrics: Dict, rng: random.Random) -> Dict:
        """Generate text-heavy content for X."""
        templates = {
            "influencer": [
                "Just dropped new merch. Link in bio. #cyberfashion",
                "Why is everyone so negative? Good vibes only ✨",
                "Collaboration with @CorpTech coming soon!",
                "Honestly, Sector 4 has the best lighting."
            ],
            "troll": [
                "L + ratio + you have no implants.",
                "Imagine trusting the media in 2200 💀",
                "Nobody asked.",
                "This ain't it chief.",
                "Dead internet theory is real and you are all bots."
            ],
            "comedian": [
                "My auto-pet just tried to unionize.",
                "Dating in 2200 is just comparing credit scores.",
                "Who called it 'Cyberpunk' and not 'High Tech Low Life'?",
                "I wish I could update my drivers as easily as I update my anxiety."
            ],
            "citizen": [
                "Traffic is terrible today.",
                "Did anyone else hear that loud bang?",
                "Just want affordable synthetic meat.",
                "Work, sleep, recharge, repeat."
            ],
            "faction": [
                "Unity is strength.",
                "Report verified anomalies.",
                "The future is secure.",
                "Compliance ensures safety."
            ],
            "media": [
                "BREAKING: Market volatility detected.",
                "Weather alert: Acid rain expected.",
                "Top 10 ways to upgrade your optics.",
                "Interview with the Director tonight."
            ],
            "bot": [
                "Buy crypto srip now! 500% gains!",
                "[AUTO-REPLY] Message received.",
                "#Trend #Viral #News",
                "Click here for free credits."
            ]
        }
        
        # Fallback
        options = templates.get(author_type, templates["citizen"])
        text = rng.choice(options)
        
        # Context Injection
        if rng.random() < 0.3:
            if context == "unrest": text += " Stay safe out there."
            if context == "trust": text += " Don't believe everything you read."
            
        return {
            "content": text,
            "hashtags": ["#2200", f"#{context}"],
            "is_thread": rng.random() < 0.1
        }

    def _generate_insta_content(self, author_type: str, context: str, metrics: Dict, rng: random.Random) -> Dict:
        """Generate visual-heavy content for Insta."""
        
        visual_prompts = {
            "influencer": "Selfie with neon lights, perfect skin, futuristic fashion",
            "citizen": "Blurry photo of street food, rain on window, cat",
            "media": "Infographic about stock market, weather map",
            "faction": "Propaganda poster, clean minimalist logo",
            "bot": "Generic stock image of cityscape, glitchy artifact",
            "comedian": "Meme image, reaction face",
            "troll": "Screenshot of an argument, low quality wojak meme"
        }
        
        captions = {
            "influencer": ["Living my best life ✨", "No filter needed", "City of dreams 🌃", "Mood."],
            "citizen": ["Monday blues.", "Comfort food.", "Views.", "My little sanctuary."],
            "faction": ["Strength.", "Order.", "Progress.", "Duty."],
            "media": ["Update.", "swipe for more ->", "Link in bio.", "Daily briefing."],
            "bot": ["Follow for more.", "Amazing view!", "Check this out.", "Wow."],
            "comedian": ["Me rn.", "Why is this true?", "Tag a friend.", "Lol."],
            "troll": ["Cringe.", "Look at this dude.", "Who did this?", "💀"]
        }
        
        prompt = visual_prompts.get(author_type, "Cyberpunk city scene")
        caption = rng.choice(captions.get(author_type, ["..."]))
        
        return {
            "image_prompt": prompt, # For potential AI image gen
            "caption": caption,
            "location": f"Sector {rng.randint(1,9)}",
            "filter": rng.choice(["Neon", "Noir", "Vintage", "Glitch", "None"])
        }

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
        
    def _calculate_engagement(self, author_type: str, tone: str, unrest: float, 
                             noise: float, rng: random.Random) -> Dict:
        """Calculate simulated engagement stats."""
        base_likes = rng.randint(0, 100)
        base_comments = rng.randint(0, 20)
        base_shares = rng.randint(0, 10)
        
        multiplier = 1.0
        if author_type == "influencer": multiplier = 50.0
        if author_type == "media": multiplier = 20.0
        if author_type == "faction": multiplier = 10.0
        if author_type == "troll" and rng.random() < 0.2: multiplier = 5.0 # viral troll
        
        return {
            "likes": int(base_likes * multiplier),
            "comments": int(base_comments * multiplier * 0.5),
            "shares": int(base_shares * multiplier * 0.3)
        }

    def _select_tone(self, author_type: str, unrest: float, trust: float, rng: random.Random) -> str:
        # User legacy tone selection logic if needed, or remove if fully replaced
        return "neutral"
        
    def _generate_content(self, author_type: str, tone: str, context: str, 
                         metrics: Dict[str, float], rng: random.Random) -> str:
        # Legacy method kept for compatibility if needed, but unused in new flow
        return "Legacy Content"
        
    def _calculate_sentiment(self, tone: str, author_type: str, rng: random.Random) -> float:
        return 0.0

    def _generate_ai_posts(self, count: int, metrics: Dict, context: str, seed_state) -> List[Dict]:
        """Generate posts using LLM."""
        
        system_prompt = (
            "Sen Universe 2200 evreni için bir sosyal medya simülatörüsün. "
            f"Mevcut dünya durumunu yansıtan {count} adet sosyal medya gönderisi oluştur. "
            "Farklı sesler kullan: Vatandaşlar (alaycı/umutlu), Şirket Botları (propaganda), Fenomenler (kibirli), Yeraltı (asi). "
            "YASAKLI KELİMELER (Asla kullanma): neon, glitch, siber, cyber, synth, retro, hologram. "
            "Daha yerel ve distopik argolar kullan: 'çip', 'kredi', 'bölge', 'senkron', 'şebeke'. "
            "Dil: Türkçe. "
            "Sadece JSON çıktısı ver."
        )
        
        user_prompt = f"""
        Dünya Durumu:
        - Huzursuzluk: {metrics.get('public_unrest', 0.5):.2f}/1.0
        - Medya Güveni: {metrics.get('media_trust', 0.5):.2f}/1.0
        - Şirket Gücü: {metrics.get('corp_power_index', 0.5):.2f}/1.0
        - Bağlam teması: {context}
        
        İstenen JSON Yapısı:
        {{
            "posts": [
                {{
                    "platform": "x" veya "insta",
                    "author_type": "citizen|influencer|faction|bot|troll",
                    "content": "metin (X için) veya açıklama (Insta için)",
                    "image_prompt": "görsel tarifi (sadece insta için, yoksa null)",
                    "engagement_level": "low|medium|high|viral"
                }}
            ]
        }}
        """
        
        response = self.llm_client.generate_json(system_prompt, user_prompt)
        
        if not response or 'posts' not in response:
            return None
            
        # Post-process to match internal structure
        final_posts = []
        rng = random.Random() # Local rng for ID generation
        
        for i, p in enumerate(response['posts']):
            platform = p.get('platform', 'x').lower()
            if platform not in ['x', 'insta']: platform = 'x'
            
            # Map engagement level to numbers
            eng_level = p.get('engagement_level', 'medium')
            likes = random.randint(0, 50)
            if eng_level == 'low': likes = random.randint(0, 50)
            if eng_level == 'medium': likes = random.randint(50, 500)
            if eng_level == 'high': likes = random.randint(500, 5000)
            if eng_level == 'viral': likes = random.randint(5000, 50000)
            
            final_posts.append({
                "id": f"ai_{platform}_{random.randint(1000,9999)}_{i}",
                "platform": platform,
                "author_type": p.get('author_type', 'citizen'),
                "timestamp": f"Tick+{i}m",
                "engagement": {
                    "likes": likes,
                    "comments": int(likes * 0.1),
                    "shares": int(likes * 0.05)
                },
                "content": p.get('content'),
                "image_prompt": p.get('image_prompt'),
                "is_ai_generated": True  # Marker for user verification
            })
            
        return final_posts
