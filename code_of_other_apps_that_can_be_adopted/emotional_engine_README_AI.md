# emotional_engine.py — README_AI

## Purpose

Tier 2 Emotional Engine. Models per-character emotional states as weighted channels
(joy, fear, anger, sadness, trust, disgust, anticipation, surprise) plus stress
accumulation. Stimuli extracted from narrative text shift channel values; channels
decay toward zero over turns.

Designed to make NPC behaviour and narration emotionally consistent with what has
actually happened in the story, not just the base character sheet.

## Key Components

### `EmotionalProfile` (dataclass)
Per-character snapshot: `channels: Dict[str, float]` (OCEAN-style mapped to Plutchik
wheel), `stress: float`, `dominant_emotion: str`.

### `EmotionalEngine`
Core computation:
- `process_stimuli(text, character_id)` — extract emotion signals from narrative text
- `apply_decay()` — decay all channels by `decay_rate` each turn
- `compute_impact(stimulus)` — apply fear/chronotype coupling, gender weight modifiers
- `get_state(character_id)` — return current `EmotionalProfile`

### `StressAccumulator`
Tracks cumulative stress per entity. Fires threshold events at configurable levels
(default: 25, 50, 75). Attached to characters and player.

### `EMOTION_KEYWORDS`
Large keyword→channel mapping used for stimulus extraction from free text.

## Integration

- Called in `core/engine.py` turn loop after narrative generation
- `build_emotional_context()` in `ai/prompt_builder.py` renders the state into prompts
- `/emotions` and `/stress` debug commands in `main.py`

## Config knobs (`config.yaml`)
```yaml
emotion_system:
  enabled: true
  max_channel_intensity: 3.0
  global_decay_floor: 0.01
  gender_weight_strength: 1.0
  stress_gain_multiplier: 1.0
  stress_event_thresholds: [25, 50, 75]
```

---
**Last Updated**: 2026-03-14 | v8.0.0
