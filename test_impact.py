"""
Test Social Impact Processor
"""
from content.social_impact import SocialImpactProcessor
from core.state import WorldState
import json

# 1. Setup Mock World State
initial_state = {
    "public_unrest": 0.5,
    "media_trust": 0.5,
    "surveillance_level": 0.5,
    "information_noise": 0.1
}
world = WorldState(initial_state)
processor = SocialImpactProcessor()

print("--- Initial State ---")
print(world.to_dict())

# 2. Test Case: Riot + Crypto-Authoritarian AI Reply
post = {"id": "post_riot_01", "content": "Down with the system!"}
comments_riot = [
    {"content": "Riot in the streets now!"},
    {"content": "Burn it all down!"},
    {"content": "They are watching us, fight back!"} # Distrust + Unrest
]
ai_reply_auth = {"content": "⚠️ VIOLATION DETECTED. User behavior logged for review."}

print("\n--- Applying Impact: Riot Scenario ---")
world = processor.apply_impact(post, comments_riot, ai_reply_auth, world)

print("--- Updated State ---")
print(world.to_dict())

# Check Traceability
print("\n--- Last Effect Logged ---")
print(json.dumps(world.last_effects[-1], indent=2))

# 3. Test Case: Calm + Bureaucratic Reply
post2 = {"id": "post_calm_02", "content": "Just stay calm."}
comments_calm = [
    {"content": "We need to have patience."},
    {"content": "Let's plan our next move quietly."}
]
ai_reply_bureau = {"content": "Feedback processed. Ticket closed."}

print("\n--- Applying Impact: Calm Scenario ---")
world = processor.apply_impact(post2, comments_calm, ai_reply_bureau, world)

print("--- Updated State ---")
print(world.to_dict())
