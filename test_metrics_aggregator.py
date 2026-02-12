"""
Test World Metrics Aggregator
"""
from core.metrics_aggregator import aggregate_metrics
from core.state import WorldState

def test_aggregator():
    print("=== Testing World Metrics Aggregator ===\n")
    
    # Setup mock world state
    ws_data = {
        'public_unrest': 0.7,
        'media_trust': 0.2,
        'corp_power_index': 0.8,
        'surveillance_level': 0.6
    }
    
    # 1. Test with Dict input
    print("1. Testing with Dict input:")
    result = aggregate_metrics(ws_data)
    print(result)
    assert result['public_unrest'] == 0.7
    assert result['corporate_power'] == 0.8
    assert result['surveillance_index'] == 0.6
    # State control should be (0.6 + (1-0.8))/2 = 0.4
    print(f"State Control (Expected ~0.4): {result['state_control']}")
    
    # 2. Test with Object input
    print("\n2. Testing with Object input:")
    ws_obj = WorldState(ws_data)
    result_obj = aggregate_metrics(ws_obj)
    print(result_obj)
    assert result_obj['public_unrest'] == 0.7
    
    # 3. Test with Faction Data
    print("\n3. Testing with Faction Data:")
    factions = {"State": 80, "Corporate": 40, "Civic": 20}
    result_fac = aggregate_metrics(ws_obj, faction_influence=factions)
    print(result_fac)
    assert result_fac['top_faction'] == "State"
    # State control should be (0.6 + 0.8)/2 = 0.7
    print(f"State Control with Faction (Expected 0.7): {result_fac['state_control']}")
    
    # 4. Test Overrides
    print("\n4. Testing Overrides:")
    result_over = aggregate_metrics(ws_obj, unrest_level=0.9)
    print(result_over)
    assert result_over['public_unrest'] == 0.9
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_aggregator()
