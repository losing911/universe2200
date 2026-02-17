"""
Population Simulation Engine

Simulates 1000 synthetic users living in the 2200 Universe.
Generates daily activity influenced by WorldState with realistic distributions.
"""

import random
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Any

# -------------------------------------------------------
# 1. USER PROFILE MODEL
# -------------------------------------------------------

@dataclass
class UserProfile:
    """
    Represents a synthetic user profile.
    """
    user_id: str
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

    def __init__(self, size: int = 1000, seed: int = 42):
        """
        Initialize population engine.
        
        Args:
            size: Number of users (default 1000)
            seed: Random seed for determinism (default 42)
        """
        self.seed = seed
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
        
        Distribution:
        - 60% passive (no action)
        - 30% reaction (like)
        - 8% comment
        - 2% create post
        
        Args:
            world_state: Metrics dict
            posts: Available posts
            tick_seed: Deterministic seed (REQUIRED for runtime execution)
            
        Returns:
            List of action dictionaries
        """
        actions = []
        
        # RNG Setup - ALWAYS use tick_seed for deterministic runtime execution
        # Fallback to _create_daily_rng only for standalone testing
        if tick_seed is not None:
            daily_rng = random.Random(tick_seed)
        else:
            # Fallback for manual/test calls without tick_seed
            daily_rng = self._create_daily_rng(world_state, posts)
            
        # Extract world metrics
        public_unrest = world_state.get("public_unrest", 0.0)
        media_trust = world_state.get("media_trust", 0.5)
        surveillance = world_state.get("surveillance_level", 0.0)
        
        for user in self.population:
            # ---------------------------------------------------
            # HIERARCHICAL ACTION DECISION
            # ---------------------------------------------------
            # Base activity probability influenced by user's activity_level
            # This determines IF they do anything at all today
            
            base_activity = user.activity_level
            
            # Surveillance dampens activity
            if surveillance > 0.5:
                base_activity *= (1.0 - surveillance * 0.3)
            
            # Roll to see if user is active today
            if daily_rng.random() > base_activity:
                # 60%+ of users are passive (lurkers)
                continue
            
            # User is active - decide what action
            # Distribution: 75% reaction, 20% comment, 5% post
            # (These are conditional on being active)
            
            action_roll = daily_rng.random()
            
            # ---------------------------------------------------
            # 1. CREATE POST (5% of active users = ~2% overall)
            # ---------------------------------------------------
            if action_roll < 0.05:
                # Calculate category weights with world modifiers
                cat_weights = []
                
                for cat in self.POST_CATEGORIES:
                    base_weight = self.CATEGORY_WEIGHTS.get(cat, 0.01)
                    
                    # World State Modifiers
                    if cat == "political":
                        if public_unrest > 0.6:
                            base_weight += 0.05  # +5% for political
                        if surveillance > 0.7:
                            base_weight *= 0.5   # -50% silencing effect
                    
                    if cat == "conspiracy":
                        if media_trust < 0.3:
                            base_weight += 0.05  # +5% for conspiracy
                    
                    cat_weights.append(base_weight)
                
                # Normalize weights
                total_weight = sum(cat_weights)
                if total_weight > 0:
                    cat_weights = [w / total_weight for w in cat_weights]
                
                # Select category
                category = daily_rng.choices(self.POST_CATEGORIES, weights=cat_weights, k=1)[0]
                
                # Select content
                content_list = self.CONTENT_BANKS.get(category, ["Generic content."])
                content = daily_rng.choice(content_list)
                
                actions.append({
                    "type": "create_post",
                    "user_id": user.user_id,
                    "category": category,
                    "content": content,
                    "timestamp": "now"
                })
                continue  # One action per day
                
            # ---------------------------------------------------
            # 2. INTERACT WITH EXISTING POSTS
            # ---------------------------------------------------
            if not posts:
                continue
            
            # Select a random post to interact with
            target_post = daily_rng.choice(posts)
            pid = target_post.get("id", "unknown")
            
            # 20% comment (of active users)
            if action_roll < 0.25:
                # Determine sentiment
                sentiment = "neutral"
                if user.aggression_level > 0.7:
                    sentiment = "aggressive"
                elif user.trust_in_media < 0.3 or media_trust < 0.3:
                    sentiment = "distrust"
                
                # Pick content
                if sentiment == "aggressive":
                    txt = daily_rng.choice(self.COMMENTS_AGGRESSIVE)
                elif sentiment == "distrust":
                    txt = daily_rng.choice(self.COMMENTS_DISTRUST)
                else:
                    txt = daily_rng.choice(self.COMMENTS_NEUTRAL)
                    
                actions.append({
                    "type": "comment",
                    "user_id": user.user_id,
                    "post_id": pid,
                    "content": txt,
                    "faction": user.faction
                })
            else:
                # 75% reaction (like) - most common action
                actions.append({
                    "type": "reaction",
                    "reaction": "like",
                    "user_id": user.user_id,
                    "post_id": pid
                })

        return actions

    def generate_daily_activity(self, *args, **kwargs) -> List[Dict]:
        """Wrapper ensuring legacy calls still work but return new format."""
        return self.generate_daily_actions(*args, **kwargs)
