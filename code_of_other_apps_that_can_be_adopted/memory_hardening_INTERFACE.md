# memory_hardening.py — INTERFACE

## `DriftVector` (dataclass)

### Fields
`character_id: str`, `turn_evaluated: int`, `dimension_deltas: Dict[str, float]`,
`dominant_drift: Optional[str]`, `magnitude: float`, `narrative_summary: str`

### `is_significant(threshold: float = 0.25) -> bool`
Returns True if `magnitude >= threshold`.

---

## `IdentityDriftChecker`

### `__init__(memory_manager, config: Optional[Dict])`
Reads `config["memory_hardening"]["identity_drift"]`. Attaches to an `EnhancedMemoryManager`.

### `evaluate_character(character_id, current_turn, base_traits) -> Optional[DriftVector]`
Returns a significant `DriftVector` if drift detected on a check-interval turn, else None.
Only runs when `current_turn % CHECK_INTERVAL == 0`.

### `get_drift_history(character_id) -> List[DriftVector]`
Returns all recorded significant drift vectors for a character.

---

## `infer_scene_type(text: str) -> str`

Classify text into one of: `"combat"`, `"death"`, `"betrayal"`, `"oath"`,
`"ritual"`, `"revelation"`, `"commerce"`, `"travel"`, `"dialogue"`, `"idle"`.

---

## `ElasticWindowCalculator`

### `__init__(config: Optional[Dict])`
Reads `config["memory_hardening"]["elastic_memory"]`.

### `compute(chaos_factor, dominant_emotion_intensity, scene_type, turn_rate_of_change) -> int`
Returns an integer window size in `[MIN_WINDOW, MAX_WINDOW]`.

---
**Contract Version**: 1.0 | 2026-03-14
