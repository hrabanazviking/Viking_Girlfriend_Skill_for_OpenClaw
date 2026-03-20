# memory_hardening.py — README_AI

## Purpose

T3-B Memory Hardening — two subsystems that harden the memory layer:

**T6 — Identity Drift Detection** (arXiv:2603.09043)
Periodically compares a character's accumulated event history against their base YAML
personality traits. Produces a `DriftVector` when meaningful divergence is found.
Significant drift is injected into the AI prompt as a `[CHARACTER EVOLUTION NOTE]` so
the LLM reflects the character's lived experience. Never modifies base YAML.

**T2 — Elastic Memory Windows** (arXiv:2603.09716)
Computes a dynamic retrieval window size based on chaos_factor, emotional intensity,
and inferred scene type. Expands context during combat/death scenes; compresses during
idle travel. Integrated into `EnhancedMemoryManager` and `MemoryQueryEngine`.

## Key Components

### `DRIFT_SIGNALS` (dict)
Maps 20 lowercase narrative keywords to OCEAN-style personality dimension deltas.
Example: `"fled" → {"courage": -0.10}`.

### `DriftVector` (dataclass)
Quantified identity drift: `character_id`, `dimension_deltas`, `dominant_drift`,
`magnitude`, `narrative_summary`. Call `is_significant(threshold)` to test.

### `IdentityDriftChecker`
Runs every `CHECK_INTERVAL` turns. Scans last `LOOKBACK_TURNS` events. Returns a
`DriftVector` only when magnitude ≥ `significance_threshold`. Never raises.

### `SCENE_KEYWORDS` / `infer_scene_type(text)`
Classifies free text into: combat, death, betrayal, oath, ritual, revelation,
commerce, travel, dialogue, idle. Priority order: combat → death → ... → idle.

### `ElasticWindowCalculator`
Formula: `BASE_WINDOW × scene_mult × chaos_mult × emotion_mult × change_mult`
Clamped to `[MIN_WINDOW=5, MAX_WINDOW=40]`. Config-driven and disable-safe.

## Integration

- `EnhancedMemoryManager.check_identity_drift()` — calls `IdentityDriftChecker`
- `EnhancedMemoryManager.get_full_context_for_ai()` — uses `_elastic_window()`
- `MemoryQueryEngine.query_turn_context()` — accepts `game_state` for elastic limit
- `PromptBuilder.build_identity_drift_notes()` — injects drift as `[CHARACTER EVOLUTION NOTE]`

## Config knobs (`config.yaml`)
```yaml
memory_hardening:
  identity_drift:
    enabled: true
    check_interval_turns: 20
    lookback_turns: 30
    significance_threshold: 0.25
    inject_into_prompt: true
  elastic_memory:
    enabled: true
    base_window: 15
    min_window: 5
    max_window: 40
```

---
**Last Updated**: 2026-03-14 | v8.0.0
