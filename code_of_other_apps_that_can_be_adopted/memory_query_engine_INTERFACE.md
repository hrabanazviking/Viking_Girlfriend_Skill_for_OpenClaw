# memory_query_engine.py — INTERFACE

## Class: `MemoryQueryEngine`

### `__init__(muninn: Any)`
Accepts any object whose `retrieve(memory_type, top_k)` signature matches Muninn's API.

### `query_turn_context(turn_number, limit=None, game_state=None) -> Dict[str, List[Dict]]`
Return `{"events": [...], "emotional_state": [...], "scene_context": [...]}` for a turn.
If `game_state` is provided and `limit` is not set, computes an elastic limit from
chaos_factor, dominant_emotion_intensity, and last_action.

### `query_character_development(character_id) -> Dict[str, Any]`
Returns `{"skill_progression", "relationship_evolution", "emotional_patterns", "narrative_arc"}`.

### `query_world_state(location) -> Dict[str, Any]`
Returns `{"location_history", "active_factions", "recent_events"}`.

### `query_relationship_history(char1, char2) -> List[Dict]`
Chronological relationship events between two characters.

### `query_emotional_patterns(character_id) -> List[Dict]`
Returns `[{"emotion": str, "count": int}, ...]` frequency list.

### `query_semantic(query_text, memory_type, limit) -> List[Dict]`
Free-text semantic retrieval against Muninn.

---

## Module Function

### `_get_nested(obj, dotted_key) -> Any`
Traverse nested mapping with dot-separated key. Returns None on missing keys.

---
**Contract Version**: 1.0 | 2026-03-14
