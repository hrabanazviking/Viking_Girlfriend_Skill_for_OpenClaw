# memory_query_engine.py — README_AI

## Purpose

Unified structured query surface over the Muninn memory raven. Translates dot-notation
filter predicates and semantic queries into `Muninn.retrieve()` calls, applying
additional filter logic (nested-field matching, list-membership) that Muninn's own
API cannot express.

All subsystems that need to read memory should go through this class rather than
calling Muninn directly. Returns plain dicts (node content), not `MemoryNode` objects,
so callers stay decoupled from storage internals.

**T3-B addition:** `query_turn_context()` now accepts an optional `game_state` dict;
when provided, it computes an elastic retrieval limit via `ElasticWindowCalculator`
based on chaos, emotion, and inferred scene type.

## Classes

### `MemoryQueryEngine`
Wraps a `Muninn` instance. All queries go through `_query()` which handles `top_k`
capping and safe attribute access.

## Key query methods

| Method | Returns | Use case |
|---|---|---|
| `query_turn_context(turn, game_state)` | events + emotional_state + scene_context | Per-turn replay |
| `query_character_development(char_id)` | skill + relationship + arc + patterns | Character arc review |
| `query_world_state(location)` | location history + active factions | Scene setup |
| `query_relationship_history(char1, char2)` | chronological relationship events | Dialogue context |
| `query_emotional_patterns(char_id)` | emotion frequency map | Drift analysis |

## Dependencies
- Requires a `Muninn` instance (from `yggdrasil/ravens/`)
- T3-B: lazily imports `ElasticWindowCalculator` and `infer_scene_type` from `systems/memory_hardening.py`

---
**Last Updated**: 2026-03-14 | v8.0.0
