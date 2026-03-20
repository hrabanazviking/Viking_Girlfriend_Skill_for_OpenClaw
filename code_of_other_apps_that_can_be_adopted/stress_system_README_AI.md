# stress_system.py — README_AI

## Purpose

Tracks cumulative stress per entity (player and NPCs). Stress accumulates from
traumatic events, combat, betrayal, prolonged hardship. When it crosses configurable
thresholds, it triggers stage events that feed into narration and dialogue.

Closely coupled with `EmotionalEngine` — stress feeds the fear/sadness channels and
modulates how characters respond in high-pressure scenes.

## Key Components

### `StressAccumulator` (dataclass)
Per-entity stress tracker: `stress_level` (0–100), `threshold_events` list,
`last_event_turn`.

### `StressSystem`
- `apply_stress(entity_id, amount)` — add stress, return threshold event if crossed
- `reduce_stress(entity_id, amount)` — natural recovery
- `get_or_create(entity_id)` — lazy-init accumulator
- `stage_for_stress(level)` — maps 0–100 to calm/tense/strained/breaking/crisis
- `tick_decay(entity_id)` — called each turn for passive recovery

## Integration

- `core/engine.py` calls `StressSystem.apply_stress()` when trauma events are logged
- `ai/prompt_builder.py` `build_emotional_context()` reads stress stage into narration
- `/stress` debug command in `main.py` shows current level and stage bar

## Config knobs
Thresholds and multiplier live in `emotion_system` block:
```yaml
emotion_system:
  stress_gain_multiplier: 1.0
  stress_event_thresholds: [25, 50, 75]
```

---
**Last Updated**: 2026-03-14 | v8.0.0
