import os
import sys
import json
from pathlib import Path

# Add project root to path
# Add project root to path
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

from core.llm_client import LLMClient, LLMConfig
from content.news_generator import generate_news
from content.social_media_generator import SocialMediaGenerator

def test_ai_generation():
    print("🧪 Verifying AI Content Generation...")
    
    # Load .env explicitly
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
    
    # Check API Key
    api_key = os.getenv("LLM_API_KEY")

    # MOCK CLIENT if no API key
    if not api_key:
        print("⚠️  No API Key found. Using MOCK Client to verify prompt logic.")
        
        class MockLLMClient:
            def __init__(self):
                self.client = True # Fake it
                
            def generate_json(self, system, user):
                print(f"\n[MOCK] System Prompt:\n{system}")
                # print(f"[MOCK] User Prompt:\n{user}")
                
                # Validation checks for strict constraints
                forbidden_words = ["neon", "glitch", "siber", "cyber", "synth", "retro", "hologram"]
                found_system = [w for w in forbidden_words if w in system.lower()]
                
                # The prompt SHOULD contain forbidden words (to forbid them)
                if found_system:
                     print(f"✅ System prompt correctly includes forbidden words list.")
                else:
                     print(f"⚠️  WARNING: System prompt does NOT explicitly list forbidden words.")
                
                if "türkçe" not in system.lower():
                     print(f"❌ ERROR: Protocol does not match 'Turkish' requirement")
                else:
                     print(f"✅ Protocol matches 'Turkish' requirement")
                
                # Retuen dummy response
                if "haber" in system.lower():
                    return {
                        "headline": "Sektör 7'de Su Kesintisi Protestoları Büyüyor",
                        "summary": "Su dağıtım şebekesindeki arızalar nedeniyle Sektör 7 sakinleri sokağa döküldü.",
                        "bias_score": -0.5,
                        "impact_level": "medium",
                        "source": "Bağımsız"
                    }
                elif "sosyal medya" in system.lower():
                    return {
                        "posts": [
                            {
                                "platform": "x",
                                "author_type": "citizen",
                                "content": "Su yoksa hayat yok. #Sektör7",
                                "engagement_level": "medium"
                            }
                        ]
                    }
                return {}

        client = MockLLMClient()
    else:
        # Setup Client
        config = LLMConfig(provider="openai", api_key=api_key)
        client = LLMClient(config)
    
    if not hasattr(client, 'client') and not hasattr(client, 'generate_json'):
        print("❌ Failed to initialize LLM Client")
        return

    # 1. Test news_generator (Active Path)
    print("\n📰 Testing News Generator (news_generator.py)...")
    
    # ContentPipeline uses dicts for events, not Event objects
    event_dict = {
        "type": "unrest_spike",
        "severity": "high",
        "value": 0.8,
        "description": "Rising unrest in Sector 7"
    }

    metrics = {
        "public_unrest": 0.8,
        "media_trust": 0.2,
        "surveillance_level": 0.7, 
        "corp_power_index": 0.9
    }
    
    try:
        # Pass llm_client via kwargs as ContentPipeline does? 
        # Actually generate_news calls _generate_ai_news if llm_client is passed
        news = generate_news(event_dict, metrics, seed=42, llm_client=client)
        print(f"✅ News Generated:\nHeadline: {news.get('headline')}\nSummary: {news.get('summary')}")
            
    except Exception as e:
        print(f"❌ News Generation Failed: {e}")

    # 2. Test SocialMediaGenerator
    print("\n📱 Testing SocialMediaGenerator...")
    social_gen = SocialMediaGenerator(llm_client=client)
    
    try:
        posts = social_gen._generate_ai_posts(
            count=3,
            metrics=metrics,
            context="unrest",
            seed_state=None
        )
        
        if posts:
            print(f"✅ Generated {len(posts)} posts:")
            for p in posts:
                print(f"   [{p['platform']}] ({p['author_type']}): {p['content']}")
        else:
            print("❌ No posts generated.")
            
    except Exception as e:
        print(f"❌ Social Generation Failed: {e}")

if __name__ == "__main__":
    test_ai_generation()
