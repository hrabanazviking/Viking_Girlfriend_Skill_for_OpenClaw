# memory_system.py — INTERFACE.md

## Class: `TurnMemory`

Memory of a single turn.

### `to_dict()`

### `from_dict(cls, data)`

## Class: `SessionMemory`

Complete memory for a session.

### `add_turn(turn)`
Add a turn to memory, managing the tiers.

### `get_context_for_ai()`
Get memory context to pass to AI each turn.

### `to_dict()`

### `from_dict(cls, data)`

## Class: `MemorySystemV3`

Enhanced memory system with AI-powered summarization.

### `start_session(session_id, player_character)`
Start a new memory session.

### `load_session(session_id)`
Load memory for a session.

### `save_session()`
Save current memory to disk.

### `record_turn(turn_number, player_action, ai_response, rune_data, location, sub_location, npcs_involved, combat, quest_updates, important_events)`
Record a turn in memory.

Args:
    turn_number: Current turn number
    player_action: What the player did
    ai_response: The AI's full response
    rune_data: Rune information if drawn
    location: Current city/region
    sub_location: Current sub-location
    npcs_involved: NPCs who appeared this turn
    combat: Whether combat occurred
    quest_updates: Any quest changes
    important_events: Major events to remember

### `get_context()`
Get memory context for AI.

### `add_key_fact(fact)`
Add a key fact manually.

### `add_relationship(npc, relationship)`
Track a relationship.

### `update_narrative(narrative)`
Update the running narrative summary.

### `get_full_history()`
Get complete session history for export.

## Class: `AISummarizer`

Uses the game's AI to generate summaries.

### `summarize(text, max_length)`
Generate a brief summary of text.

### `generate_narrative_summary(memory)`
Generate a narrative summary of the session so far.

---
**Contract Version**: 1.0 | v8.0.0
