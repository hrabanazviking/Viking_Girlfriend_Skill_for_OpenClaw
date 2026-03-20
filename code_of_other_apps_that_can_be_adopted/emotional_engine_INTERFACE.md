# emotional_engine.py — INTERFACE

## Class: `EmotionalProfile`
Dataclass per-character emotional snapshot.

### Fields
`character_id: str`, `channels: Dict[str, float]`, `stress: float`,
`dominant_emotion: str`, `turn_last_updated: int`

---

## Class: `EmotionalEngine`

### `__init__(config: Optional[Dict])`
Reads `config["emotion_system"]`.

### `process_stimuli(text: str, character_id: str) -> EmotionalProfile`
Extract emotion signals from `text`, apply to `character_id`'s profile.

### `apply_decay(character_id: str) -> None`
Decay all emotion channels toward zero by `decay_rate`.

### `get_state(character_id: str) -> EmotionalProfile`
Return current profile (creates default if not exists).

### `get_dominant_emotion(character_id: str) -> str`
Return the highest-magnitude channel name.

### `intensity_label(value: float) -> str`
Module-level helper: maps float magnitude to label (calm / mild / moderate / intense / overwhelming).

---

## Class: `StressAccumulator`

### Fields
`entity_id: str`, `stress_level: float`, `threshold_events: List[str]`

---

## Class: `StressSystem`

### `apply_stress(entity_id, amount) -> Optional[str]`
Add stress; returns threshold event string if a threshold was crossed, else None.

### `get_or_create(entity_id) -> StressAccumulator`

### `stage_for_stress(level) -> str`
Returns: `"calm"`, `"tense"`, `"strained"`, `"breaking"`, or `"crisis"`.

---
**Contract Version**: 1.0 | 2026-03-14
