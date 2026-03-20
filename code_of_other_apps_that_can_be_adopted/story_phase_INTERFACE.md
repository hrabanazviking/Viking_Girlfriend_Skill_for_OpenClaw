# story_phase.py — INTERFACE.md

## Class: `StoryPhase`

Archetypal arc layer — the monomyth cycle shaping narrative momentum.

### `current_phase()`

### `phase_name()`

### `phase_description()`

### `update(turn_count, force_advance)`
Advance the story phase if enough turns have passed.

### `build_context()`
Build the story phase context block for prompt injection.

### `to_dict()`
Serialize for save.

### `from_dict(data)`
Restore from save.

---
**Contract Version**: 1.0 | v8.0.0
