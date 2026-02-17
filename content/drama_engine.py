"""
Drama Engine for Universe 2200

Generates non-political social scenarios, influencer drama, and viral trends.
Injects "human" chaos into the simulation.
"""

import random
from typing import List, Dict, Any

class DramaEngine:
    """
    Generates social scenarios and narrative events.
    """
    
    SCENARIOS = {
        "influencer_scandal": [
            "{actor} caught using non-organic filters on live stream.",
            "{actor} leaked private DMs mocking their fans.",
            "{actor} creates controversial holonft collection.",
            "{actor} accidentally streams their therapy session."
        ],
        "viral_trend": [
            "Users are obsessively posting pictures of {topic}.",
            "New dance craze 'The Glitch' is taking over Sector 4.",
            "Everyone is debating if {topic} is actually cake.",
            "Flash mob detected at the Neon Plaza."
        ],
        "relationship_drama": [
            "{actor} and {target} were seen arguing at the Spaceport.",
            "Rumors circulating about a secret affair between {actor} and {target}.",
            "{actor} blocked {target} on all platforms.",
            "{actor} posted a cryptic sub-tweet about loyalty."
        ]
    }
    
    TOPICS = ["old tech", "synthetic meat", "retro fashion", "government drones", "virtual pets"]
    
    def __init__(self, social_network):
        self.social_network = social_network
        
    def generate_events(self, tick: int) -> List[Dict]:
        """Generate a list of drama events for the current tick."""
        events = []
        rng = random.Random(tick + 999) # Salt
        
        # 1. Check for Relationship Events (from SocialNetworkCore)
        rel_events = self.social_network.generate_relationship_events(tick)
        for re in rel_events:
            event = {
                "type": "relationship",
                "content": re["desc"],
                "actors": re["actors"],
                "timestamp": "now"
            }
            events.append(event)
            
        # 2. Random Influencer Scandal? (5% chance)
        if rng.random() < 0.05:
            influencers = [
                uid for uid, u in self.social_network.users.items() 
                if u.get("role") == "influencer"
            ]
            
            if influencers:
                actor_id = rng.choice(influencers)
                actor_name = f"@{actor_id}" # Simplify for now
                template = rng.choice(self.SCENARIOS["influencer_scandal"])
                content = template.format(actor=actor_name)
                
                events.append({
                    "type": "scandal",
                    "content": content,
                    "actors": [actor_id],
                    "timestamp": "now"
                })
                
        # 3. Viral Trend? (10% chance)
        if rng.random() < 0.10:
            topic = rng.choice(self.TOPICS)
            template = rng.choice(self.SCENARIOS["viral_trend"])
            content = template.format(topic=topic)
            
            events.append({
                "type": "trend",
                "content": content,
                "actors": [],
                "timestamp": "now"
            })
            
        return events
