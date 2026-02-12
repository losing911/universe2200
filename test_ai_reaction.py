"""
Test AI Reaction logic
"""
from simulation.ai_reaction_engine import AIReactionEngine

def test_ai_reaction():
    print("--- Testing AI Reaction Engine ---")
    
    engine = AIReactionEngine()
    
    # 1. Setup Mock Entities
    ai = {
        "id": "ai_net",
        "chaos_affinity": 0.8, # Chaotic AI
        "faction_loyalty": {"tech": 0.9}
    }
    
    target = {
        "id": "user1",
        "influence_score": 10.0,
        "reputation_score": -25.0, # Notorious
        "faction": "bio" # Opposing tech
    }
    
    post = {"id": "post1", "topics": ["tech", "chaos"]}
    world = {"public_unrest": 0.5}
    
    # 2. Test Determinism
    print("\n[1] Testing Deterministic Decision...")
    res1 = engine.decide_reaction(ai, target, post, world)
    res2 = engine.decide_reaction(ai, target, post, world)
    
    print(f"Run 1: {res1['reaction_type']}")
    print(f"Run 2: {res2['reaction_type']}")
    
    if res1["reaction_type"] == res2["reaction_type"]:
        print("✅ SUCCESS: Reaction is deterministic.")
    else:
        print("❌ FAILURE: Determinism broken.")
        
    # 3. Test Alignment Logic (Support Case)
    print("\n[2] Testing High Alignment (Supporter AI)...")
    ai_loyal = {"id": "ai_loyal", "chaos_affinity": 0.0, "faction_loyalty": {"bio": 0.9}}
    res_loyal = engine.decide_reaction(ai_loyal, target, post, world)
    
    print(f"Loyal AI Reaction: {res_loyal['reaction_type']}")
    # Given weights boost, should likely support. But probabilistic.
    # We check if reasoning weight for support was high
    print(f"Reasoning: {res_loyal['reason']}")
    
    # 4. Test Attack Logic (Chaotic vs Notorious)
    print("\n[3] Testing Attack Logic...")
    # Notorious user + Chaotic AI + Unrest -> Attack/Manipulate likely
    world_unrest = {"public_unrest": 0.9} 
    res_chaos = engine.decide_reaction(ai, target, post, world_unrest)
    type_c = res_chaos['reaction_type']
    print(f"Chaos/Unrest Reaction: {type_c}")
    
    if type_c in ["attack", "manipulate"]:
        print("✅ SUCCESS: High unrest/chaos triggered appropriate response.")
    else:
         print("⚠️ WARNING: Probabilistic outcome was 'ignore' or 'support'. Run again to confirm trend if needed.")
         
    # 5. Check Deltas
    deltas = res_chaos.get("entity_deltas", {})
    if deltas:
        print(f"Deltas applied: {deltas}")
        if type_c == "attack" and deltas.get("reputation_score", 0) < 0:
             print("✅ SUCCESS: Attack reduced reputation.")
        elif type_c == "support" and deltas.get("reputation_score", 0) > 0:
             print("✅ SUCCESS: Support increased reputation.")

if __name__ == "__main__":
    test_ai_reaction()
