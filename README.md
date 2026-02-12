# 2200 Evreni - Simulation-Driven Living Universe

A rule-based simulation engine that creates a living fictional universe evolving through deterministic and probabilistic rules.

## Overview

2200 Evreni is an MVP simulation engine where:
- The universe evolves via rule-based simulation
- Events are generated automatically based on world state
- Data is structured for future AI integration (RAG, storytelling, social media bots, games)

## Architecture

The system has 4 conceptual layers:
1. **Lore Engine (Core Data Layer)** - World state, characters, events ✅ Implemented
2. **Simulation Engine (Rules & State Changes)** - Daily tick system ✅ Implemented
3. **AI Content Trigger Layer** - Not yet implemented
4. **Platform / User Interaction** - Not yet implemented

## Tech Stack

- **Language**: Python 3.11+
- **Storage**: JSON files (local)
- **Dependencies**: None (stdlib only)

## Project Structure

```
universe_2200/
├─ core/
│   ├─ state.py          # Global world state management
│   ├─ characters.py     # Character models
│   ├─ events.py         # Event schema and event log
│   └─ world.py          # World loader/saver (JSON persistence)
│
├─ simulation/
│   ├─ rules.py          # All simulation rules
│   ├─ engine.py         # Tick engine
│   └─ scheduler.py      # Daily simulation runner
│
├─ data/
│   ├─ world_state.json  # Current world metrics
│   ├─ characters.json   # Character data
│   └─ event_log.json    # Generated events
│
├─ main.py               # Entry point
└─ README.md             # This file
```

## How to Run

```bash
cd universe_2200
python main.py
```

This will:
1. Initialize the world (or load existing state)
2. Run 30 days of simulation
3. Generate events based on rules
4. Save all state changes to JSON files
5. Print a summary to console

## World State

The world is tracked via these metrics (0-1 range unless noted):

- `water_price_index` - Water price index (can exceed 1.0)
- `energy_price_index` - Energy price index (can exceed 1.0)
- `public_unrest` - Level of public unrest
- `media_trust` - Public trust in media
- `ai_dependency` - Society's dependency on AI
- `corp_power_index` - Corporate power influence
- `current_date` - Current simulation date (YYYY-MM-DD)

## Simulation Rules

### 1. Economy Pressure
**IF** `water_price_index > 1.5`  
**THEN** `public_unrest += 0.1`

### 2. Protest Generation (Probabilistic)
**IF** `public_unrest > 0.4`  
**THEN** Chance to generate a protest event  
Probability scales with unrest level.

### 3. Crisis Escalation
**IF** A protest event with `scale > 0.6` is generated  
**THEN** Generate a `political_crisis` event

### 4. Natural Decay
Metrics gradually return to baseline over time.

## Event Schema

Every event includes:

```python
{
  "id": "unique-uuid",
  "type": "protest | political_crisis | resource_shortage | etc.",
  "date": "YYYY-MM-DD",
  "location": "Neo Istanbul Central Square",
  "scale": 0.75,           # 0-1 range
  "visibility": 0.8,       # 0-1 range
  "description": "...",
  "canon_level": "soft",   # soft | hard | absolute
  "generated_by": "simulation_engine",
  "metadata": { ... }      # Additional context
}
```

## Extending the System

### Adding New Rules

1. Create a new rule class in `simulation/rules.py`:

```python
class MyNewRule(SimulationRule):
    def __init__(self):
        super().__init__("My New Rule")
    
    def evaluate(self, state: WorldState) -> Tuple[List[Event], dict]:
        events = []
        changes = {}
        
        # Your rule logic here
        if state.some_metric > threshold:
            changes['other_metric'] = 0.1
        
        return events, changes
```

2. Add it to the `RuleEngine` in `simulation/rules.py`:

```python
self.rules = [
    EconomyPressureRule(),
    ProtestGenerationRule(),
    MyNewRule(),  # Add here
    # ...
]
```

### Adding New Metrics

1. Add the metric to `WorldState` in `core/state.py`
2. Update `initialize_default_state()` in `core/world.py`
3. Create rules that modify the new metric

### Adding Characters

Characters are currently placeholder data. To integrate:

1. Add character data to `data/characters.json`
2. Create character-specific rules in `simulation/rules.py`
3. Reference characters in event metadata

## Output

After running, check:

- `data/world_state.json` - Updated world metrics
- `data/event_log.json` - All generated events
- Console output - Daily summaries

## Future Extensions

This MVP is designed to support:

- **AI Storytelling**: Use event_log.json as context for LLM narrative generation
- **Social Media Bots**: Auto-post events to Twitter/Discord
- **RAG Systems**: Vector DB indexing of events for AI queries
- **Game Integration**: Use events as quests/missions
- **ARG (Alternate Reality Game)**: Real-time universe that players discover

## Design Principles

✅ **Clean Code**: Readable, well-commented  
✅ **Extensible**: Easy to add rules, metrics, events  
✅ **Data-Driven**: All state in JSON for portability  
✅ **No Dependencies**: Pure Python stdlib  
✅ **AI-Ready**: Structured data for downstream AI systems

---

**Version**: 1.0.0 (MVP)  
**Last Updated**: 2207-01-01 (in-universe)
