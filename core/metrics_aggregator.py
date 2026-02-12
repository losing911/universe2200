"""
World Metrics Aggregator for Universe 2200

A pure function module that aggregates various simulation metrics into a 
consolidated summary. This module is deterministic and stateless, 
designed to provide a high-level view of the current world state.
"""

from typing import Dict, Any, Optional

def aggregate_metrics(
    world_state: Any,
    faction_influence: Dict[str, float] = None,
    unrest_level: float = None,
    surveillance_index: float = None
) -> Dict[str, Any]:
    """
    Aggregate metrics from various sources into a unified summary.
    
    Args:
        world_state: WorldState object or dictionary
        faction_influence: Dictionary mapping faction names to influence scores (0-100)
        unrest_level: Optional override for public unrest (0-1)
        surveillance_index: Optional override for surveillance level (0-1)
        
    Returns:
        Dictionary containing aggregated metrics:
        {
            "public_unrest": float,
            "media_trust": float,
            "corporate_power": float,
            "state_control": float,
            "surveillance_index": float,
            "top_faction": string
        }
    """
    # 1. Normalize Inputs
    if faction_influence is None:
        faction_influence = {}
        
    # Extract from world_state if object or dict
    if hasattr(world_state, 'public_unrest'):
        ws_unrest = world_state.public_unrest
        ws_trust = world_state.media_trust
        ws_corp = world_state.corp_power_index
        ws_surv = getattr(world_state, 'surveillance_level', 0.5)
    elif isinstance(world_state, dict):
        ws_unrest = world_state.get('public_unrest', 0.5)
        ws_trust = world_state.get('media_trust', 0.5)
        ws_corp = world_state.get('corp_power_index', 0.5)
        ws_surv = world_state.get('surveillance_level', 0.5)
    else:
        # Fallback defaults
        ws_unrest = 0.5
        ws_trust = 0.5
        ws_corp = 0.5
        ws_surv = 0.5

    # 2. Determine Values (Priotizing overrides)
    public_unrest = unrest_level if unrest_level is not None else ws_unrest
    surveillance = surveillance_index if surveillance_index is not None else ws_surv
    
    # 3. Calculate Derived Metrics
    
    # Top Faction Logic
    if faction_influence:
        top_faction = max(faction_influence, key=faction_influence.get)
    else:
        # Fallback if no data provided
        if ws_corp > 0.6:
            top_faction = "Corporate"
        elif ws_surv > 0.6:
            top_faction = "State"
        elif public_unrest > 0.6:
            top_faction = "Civic"
        else:
            top_faction = "None"
            
    # State Control Proxy
    # If "State" faction exists, normalize its influence (assuming 0-100 scale)
    state_inf = faction_influence.get("State", 0.0) / 100.0
    
    # Heuristic: State Control is high if surveillance is high + State influence is high
    # If no state influence data, rely on surveillance and (1 - corp_power)
    if "State" in faction_influence:
        state_control = (surveillance + state_inf) / 2.0
    else:
        # In a generic cyberpunk setting, State power is often inverse to Corp power
        # But also correlated with surveillance
        state_control = (surveillance + (1.0 - ws_corp)) / 2.0
        
    # Clamp results to 0.0 - 1.0
    state_control = max(0.0, min(1.0, state_control))

    # 4. Construct Output
    return {
        "public_unrest": float(round(public_unrest, 4)),
        "media_trust": float(round(ws_trust, 4)),
        "corporate_power": float(round(ws_corp, 4)),
        "state_control": float(round(state_control, 4)),
        "surveillance_index": float(round(surveillance, 4)),
        "top_faction": str(top_faction)
    }

