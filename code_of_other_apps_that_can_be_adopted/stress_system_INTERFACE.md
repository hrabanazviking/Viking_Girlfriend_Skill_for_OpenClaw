# stress_system.py — INTERFACE

## Class: `StressAccumulator` (dataclass)

### Fields
`entity_id: str`, `stress_level: float`, `threshold_events: List[str]`,
`last_event_turn: int`

---

## Class: `StressSystem`

### `__init__(config: Optional[Dict])`

### `apply_stress(entity_id: str, amount: float) -> Optional[str]`
Increase stress by `amount`. Returns threshold event label if a threshold was
crossed (e.g. `"stress_threshold_50"`), else None.

### `reduce_stress(entity_id: str, amount: float) -> None`
Decrease stress (floored at 0.0).

### `tick_decay(entity_id: str) -> None`
Passive per-turn recovery. Call once per turn per tracked entity.

### `get_or_create(entity_id: str) -> StressAccumulator`
Lazy-init accumulator for `entity_id`.

### `stage_for_stress(level: float) -> str`
Static method. Returns one of: `"calm"`, `"tense"`, `"strained"`, `"breaking"`, `"crisis"`.

---
**Contract Version**: 1.0 | 2026-03-14
