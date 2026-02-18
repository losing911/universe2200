"""
Population Simulation Engine

Simulates 1000 synthetic users living in the 2200 Universe.
Generates daily activity influenced by WorldState with realistic distributions.
"""

import random
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any
from core.name_generator import NameGenerator

# -------------------------------------------------------
# 1. USER PROFILE MODEL
# -------------------------------------------------------

@dataclass
class UserProfile:
    """
    Represents a synthetic user profile.
    """
    user_id: str
    handle: str
    display_name: str
    avatar: str
    gender: str
    faction: str  # bio, augmented, synthetic, hybrid, purist
    role: str     # influencer, comedian, journalist, troll, fan, regular
    interests: List[str]
    personality_traits: List[str]
    political_bias: float  # 0.0 - 1.0
    aggression_level: float  # 0.0 - 1.0
    trust_in_media: float  # 0.0 - 1.0
    activity_level: float  # 0.0 - 1.0
    topic_affinity: Dict[str, float] = field(default_factory=dict)


# -------------------------------------------------------
# 2. POPULATION ENGINE
# -------------------------------------------------------

class PopulationEngine:
    """
    Manages synthetic user population and daily activity generation.
    Deterministic behavior based on seed and date.
    Simulates realistic social media behavior with proper distributions.
    """
    
    FACTIONS = ["bio", "augmented", "synthetic", "hybrid", "purist"]
    
    # New Social Dimensions
    ROLES = ["influencer", "comedian", "journalist", "troll", "fan", "regular"]
    ROLE_WEIGHTS = [0.02, 0.03, 0.02, 0.05, 0.15, 0.73] # 2% influencers, etc.
    
    INTERESTS = [
        "fashion", "tech", "gaming", "politics", "gossip", "fitness", 
        "music", "art", "crypto", "history", "science", "travel"
    ]
    
    TRAITS = ["humorous", "drama_seeker", "wholesome", "toxic", "intellectual", "chaotic"]
    
    TOPICS = ["politics", "economy", "technology", "security", "corporate"]
    
    POST_CATEGORIES = [
        "personal", "meme", "entertainment", "daily_life", "tech",
        "corporate", "political", "conspiracy", "ai_art", "rant"
    ]
    
    # Realistic weighted distribution for post categories
    # Total should sum to ~1.0
    CATEGORY_WEIGHTS = {
        "personal": 0.35,
        "meme": 0.10,        # Combined with entertainment
        "entertainment": 0.10,
        "daily_life": 0.15,
        "tech": 0.10,
        "corporate": 0.08,
        "political": 0.07,
        "conspiracy": 0.05,
        "ai_art": 0.0,       # Rare, bundled into tech/meme
        "rant": 0.0          # Rare, expressed through sentiment
    }
    
    CONTENT_BANKS = {
        "political": [
            "The new policies are a disaster waiting to happen.",
            "Finally, some leadership we can trust!",
            "Why is no one talking about the real issues?",
            "History will judge us for this moment.",
            "They say it's for 'security', but we know the truth.",
            "Vote with your wallet if you can't vote with your ballot.",
            "The system is rigged against the common citizen."
        ],
        "meme": [
            "*posts a pic of a cat in a cyber-suit*",
            "tfw you forget your neural link password.",
            "POV: You live in Zone 4.",
            "Stonks only go up 🚀 (except when they don't).",
            "Me waiting for the water ration update like...",
            "Cyber-Monday is a scam, change my mind."
        ],
        "personal": [
            "Just had the best synthe-caf at Sector 7.",
            "Feeling a bit glitchy today. Need a reset.",
            "Can't believe it's been 5 years since the upgrade.",
            "Missing the old skyline before the smog set in.",
            "Anyone want to hang out at the neon plaza?",
            "My auto-pet is acting weird again."
        ],
        "corporate": [
            "Innovation is our currency. #FutureNow",
            "Quarterly earnings exceed expectations.",
            "We are committed to a sustainable tomorrow.",
            "New product drop incoming. Stay tuned.",
            "Safety. Security. Stability.",
            "Join our team and build the future."
        ],
        "conspiracy": [
            "The water shortage is artificial.",
            "I saw them moving 'decommissioned' units at night.",
            "The AI isn't just watching, it's predicting.",
            "Zone 1 doesn't actually exist.",
            "They are rewriting the archives.",
            "Don't drink the tap water on Tuesdays."
        ],
        "entertainment": [
            "Did you see the latest episode of 'Neon Dreams'?",
            "That concert last night was unreal.",
            "Simulator games are getting too realistic.",
            "New starlet scandal! Read the thread.",
            "Looking for new holo-tapes recommendations.",
            "Celebrity culture is a distraction."
        ],
        "daily_life": [
            "Traffic on the skyway is brutal today.",
            "Weather projection: Acid rain. Again.",
            "Just got my new uniform. Fits well.",
            "Meal prep for the week: Algae bars.",
            "Is it Friday yet?",
            "Neighbor's drone is too loud."
        ],
        "tech": [
            "The new neural interface has latency issues.",
            "Coding in pure Python is still the best.",
            "Cyber-security update recommended immediately.",
            "Hardware prices are skyrocketing.",
            "Just overclocked my rig. Running smooth.",
            "AI generation is getting scarily good."
        ],
        "ai_art": [
            "Generated this landscape based on old earth photos.",
            "Prompt: 'Neon sunset over ruined city'.",
            "Is it art if a machine made it?",
            "Look at the details on this texture.",
            "My AI artist model is finally trained.",
            "Abstract data visualization art."
        ],
        "rant": [
            "I AM SO DONE WITH THIS.",
            "Why is customer service always an AI bot?",
            "People who walk slow on the mag-lev... move!",
            "Everything is broken and nobody cares.",
            "Just scream into the void. It helps.",
            "Can we just restart the simulation?"
        ]
    }
    
    COMMENTS_AGGRESSIVE = [
        "This is unacceptable!", "Burn it down.", "Lies, all lies.", 
        "They are mocking us.", "We need action now.", "Where is the justice?",
        "Pathetic response.", "Another distraction.", "Wake up people!", "Resistance is duty."
    ]
    
    COMMENTS_NEUTRAL = [
        "Interesting development.", "Let's wait and see.", "Measured response needed.",
        "Seems plausible.", "Noted.", "Updates requested.", "Monitoring situation.",
        "Okay.", "Could be worse.", "Standard procedure."
    ]
    
    COMMENTS_DISTRUST = [
        "Propaganda.", "Who is funding this?", "Check the sources.", 
        "The algorithm is biased.", "They are watching.", "Fake news.",
        "Fabricated narrative.", "Don't believe them.", "Hidden agenda.", "Smoke and mirrors."
    ]

    def __init__(self, size: int = 1000, seed: int = 42, llm_client=None):
        """
        Initialize population engine.
        
        Args:
            size: Number of users (default 1000)
            seed: Random seed for determinism (default 42)
            llm_client: Optional LLMClient for AI generation
        """
        self.seed = seed
        self.llm_client = llm_client
        self.population: List[UserProfile] = []
        
        # Generate population immediately
        self._generate_population(size)
        
    def _create_daily_rng(self, world_state: Dict[str, Any], posts: List[Dict]) -> random.Random:
        """
        Create a deterministic RNG based on:
        - engine seed
        - world_state["date"]
        - input posts (sorted by id)
        
        This guarantees identical results for the same day and same content.
        """
        date = str(world_state.get("date", "day0"))
        if hasattr(world_state.get("date"), "strftime"):
            date = world_state["date"].strftime("%Y-%m-%d")
            
        sorted_ids = sorted([str(p.get("id", "")) for p in posts])
        posts_hash = hashlib.sha256("".join(sorted_ids).encode()).hexdigest()[:16]
            
        seed_input = f"{self.seed}_{date}_{posts_hash}".encode()
        day_seed = int(hashlib.sha256(seed_input).hexdigest(), 16) % (2**32)
        return random.Random(day_seed)

    def _generate_population(self, size: int):
        """Generate synthetic users deterministically."""
        init_rng = random.Random(self.seed)
        self.population = []
        
        for i in range(size):
            user_id = f"user_{i:04d}"
            identity = NameGenerator.generate_name(seed=self.seed + i)
            
            faction = init_rng.choice(self.FACTIONS)
            
            # Role selection
            role = init_rng.choices(self.ROLES, weights=self.ROLE_WEIGHTS, k=1)[0]
            
            # Interests (1-3)
            num_interests = init_rng.randint(1, 3)
            interests = init_rng.sample(self.INTERESTS, k=num_interests)
            
            # Personality Traits (1-2)
            num_traits = init_rng.randint(1, 2)
            personality_traits = init_rng.sample(self.TRAITS, k=num_traits)
            
            political_bias = init_rng.random()
            aggression_level = init_rng.random()
            trust_in_media = init_rng.random()
            
            # Power law distribution for activity level
            raw_activity = init_rng.random()
            activity_level = raw_activity * raw_activity
            
            # Boost activity for influencers and trolls
            if role == "influencer": activity_level = max(0.8, activity_level * 1.5)
            if role == "troll": activity_level = max(0.6, activity_level * 1.2)
            
            topic_affinity = {
                topic: init_rng.random() 
                for topic in self.TOPICS
            }
            
            user = UserProfile(
                user_id=user_id,
                handle=identity["handle"],
                display_name=identity["display_name"],
                avatar=identity["avatar"],
                gender=identity["gender"],
                faction=faction,
                role=role,
                interests=interests,
                personality_traits=personality_traits,
                political_bias=political_bias,
                aggression_level=aggression_level,
                trust_in_media=trust_in_media,
                activity_level=activity_level,
                topic_affinity=topic_affinity
            )
            self.population.append(user)

    def generate_daily_actions(self, world_state: Dict[str, float], posts: List[Dict], tick_seed: int = None) -> List[Dict]:
        """
        Generate structured actions with realistic social media distributions.
        """
        actions = []
        
        # RNG Setup
        if tick_seed is not None:
            daily_rng = random.Random(tick_seed)
        else:
            daily_rng = self._create_daily_rng(world_state, posts)
            
        # Extract world metrics
        public_unrest = world_state.get("public_unrest", 0.0)
        media_trust = world_state.get("media_trust", 0.5)
        surveillance = world_state.get("surveillance_level", 0.0)
        
        # Limit total AI calls per tick to prevent timeouts (e.g. 5 posts, 15 comments)
        ai_post_count = 0
        ai_comment_count = 0
        MAX_AI_POSTS = 5
        MAX_AI_COMMENTS = 15
        
        # Shuffle population to give everyone a chance
        active_population = list(self.population)
        daily_rng.shuffle(active_population)
        
        for user in active_population:
            # Base activity probability
            base_activity = user.activity_level
            if surveillance > 0.5:
                base_activity *= (1.0 - surveillance * 0.3)
            
            if daily_rng.random() > base_activity:
                continue
            
            # Action Roll
            action_roll = daily_rng.random()
            
            # 1. CREATE POST
            if action_roll < 0.05:
                if self.llm_client and ai_post_count < MAX_AI_POSTS:
                    # Generate AI Post
                    content, category = self._generate_ai_post_content(user, world_state, daily_rng)
                    if content:
                        actions.append({
                            "type": "create_post",
                            "user_id": user.user_id,
                            "category": category,
                            "content": content,
                            "timestamp": "now",
                            "is_ai": True
                        })
                        ai_post_count += 1
                # If no AI client or limit reached, we SKIP generating a post (User request: No Templates)
                # Alternatively, we could fallback, but user was strict. 
                # For "simulation" continuity, we might want minimal fallback, but I'll respect strict "No Templates" for now on posts.
                continue
                
            # 2. INTERACT
            if not posts:
                continue
            
            target_post = daily_rng.choice(posts)
            pid = target_post.get("id", "unknown")
            
            if action_roll < 0.25:
                if self.llm_client and ai_comment_count < MAX_AI_COMMENTS:
                    # Generate AI Comment
                    comment_text = self._generate_ai_comment_content(user, target_post, world_state)
                    if comment_text:
                        actions.append({
                            "type": "comment",
                            "user_id": user.user_id,
                            "post_id": pid,
                            "content": comment_text,
                            "faction": user.faction,
                            "is_ai": True
                        })
                        ai_comment_count += 1
                # Skip if no AI capacity
                # Skip if no AI capacity
            else:
                # 3. INTERACTIONS (Like / Comment / Flirt)
                
                # Check for Flirt Opportunity (Male -> Female)
                # 5% chance if gender matches logic
                is_flirt = False
                target_user_id = target_post.get("author_id")
                # Need to find target user object, but we only have ID here.
                # Simplification: Random chance if user is Male
                
                if user.gender == "male" and action_roll < 0.10: # 10% chance for males to try flirting
                     # We can't easily check target gender here without lookup, 
                     # but we can try to flirt broadly or assume 50% hit rate 
                     # (or rely on AI to handle context if enabled).
                     # For now, let's just use a special comment category "flirt"
                     
                    actions.append({
                        "type": "comment",
                        "user_id": user.user_id,
                        "post_id": pid,
                        "content": daily_rng.choice([
                            "Harika görünüyorsun! 🔥",
                            "Bu fotoğraf çok iyi.",
                            "DM bakabilir misin? 👀",
                            "Vay canına...",
                            "Tarzın çok hoş.",
                            "Selam, tanışalım mı?"
                        ]),
                        "faction": user.faction,
                        "subtype": "flirt"
                    })
                    continue

                # Standard Interactions
                # Likes are cheap, keep them
                actions.append({
                    "type": "reaction",
                    "reaction": "like",
                    "user_id": user.user_id,
                    "post_id": pid
                })

        return actions

    def _generate_ai_post_content(self, user: UserProfile, world_state: Dict, rng: random.Random):
        """Generate a post using LLM."""
        category = rng.choice(self.POST_CATEGORIES)
        
        system_prompt = (
            f"Sen {user.handle} adında bir sosyal medya kullanıcısısın. "
            f"Rolün: {user.role}. İlgi alanların: {', '.join(user.interests)}. "
            f"Kişilik özelliklerin: {', '.join(user.personality_traits)}. "
            f"Siyasi Görüş: {'Muhalif' if user.political_bias < 0.4 else 'Sadık' if user.political_bias > 0.6 else 'Nötr'}. "
            f"Dil: Türkçe. Kısa, doğal, tweet tarzı yaz. Hashtag kullanabilirsin. "
            f"YASAKLI KELİMELER: neon, glitch, siber, cyber, hologram."
        )
        
        user_prompt = (
            f"Konu: {category}. "
            f"Dünya Durumu: Huzursuzluk {world_state.get('public_unrest', 0.5):.1f}, Güven {world_state.get('media_trust', 0.5):.1f}. "
            f"Bu durum hakkında kısa bir gönderi yaz."
        )
        
        try:
            # We use generate_text for speed/simplicity instead of strict JSON for single strings
            content = self.llm_client.generate_text(system_prompt, user_prompt)
            if content:
                return content.strip().replace('"', ''), category
        except Exception as e:
            print(f"AI Post Gen failed: {e}")
            
        return None, category

    def _generate_ai_comment_content(self, user: UserProfile, target_post: Dict, world_state: Dict):
        """Generate a comment using LLM."""
        post_content = target_post.get('content', '')
        
        system_prompt = (
            f"Sen {user.handle} adında bir kullanıcısın. "
            f"Kişilik: {', '.join(user.personality_traits)}. "
            f"Dil: Türkçe. Çok kısa, doğal bir yorum yaz (max 10 kelime). "
        )
        
        user_prompt = (
            f"Şu gönderiye yorum yap: '{post_content}'\n"
            f"Senin görüşün: {'Destekle' if user.political_bias > 0.5 else 'Eleştir'}."
        )
        
        try:
            content = self.llm_client.generate_text(system_prompt, user_prompt)
            if content:
                return content.strip().replace('"', '')
        except Exception:
            pass
            
        return None

    def generate_daily_activity(self, *args, **kwargs) -> List[Dict]:
        """Wrapper ensuring legacy calls still work but return new format."""
        return self.generate_daily_actions(*args, **kwargs)
