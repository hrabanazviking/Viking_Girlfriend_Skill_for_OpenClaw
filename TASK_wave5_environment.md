# TASK: Wave 5 — Environment & Situational Presence (E-20–E-22)
**Created:** 2026-03-21
**Branch:** development
**Status:** IN PROGRESS

## Scope
Three enhancements making Sigrid's perceived world feel alive and reactive.
Note: STATUS_2026-03-21.md incorrectly listed E-23/E-24 as Wave 5 — Wave 5 is
only E-20, E-21, E-22. Wave 6 begins after E-22.

## Enhancements

| ID   | Title                    | Module(s)                                              | Status |
|------|--------------------------|--------------------------------------------------------|--------|
| E-20 | TOD Vibe Shift           | environment_mapper.py, environment.json                | DONE   |
| E-21 | Sensory Hint Layer       | environment_mapper.py, environment.json, prompt_synthesizer.py | DONE |
| E-22 | Object State Tracking    | environment_mapper.py                                  | DONE   |

## File Changes

### environment.json
- Add `vibe` + `vibe_by_tod` dict to all home_base rooms (currently missing vibe)
- Add `sensory: {smell, sound, texture}` to all rooms

### environment_mapper.py
- `EnvironmentState` gains: `current_vibe`, `tod_override`, `object_states` fields
- `get_state()` reads TOD from scheduler, resolves vibe_by_tod
- `get_sensory_hints()` returns stochastically selected 1-2 sensory channels
- `ObjectState` dataclass: object_id, room_id, state, changed_at, expires_at
- `set_object_state(room_id, object_id, state, duration_minutes)`
- `get_active_object_states(room_id)` with auto-expiry
- `session/object_states.json` persistence

### prompt_synthesizer.py
- `include_sensory: bool` config flag (default True)
- `_build_environment_block(sensory_hints)` private method
- `build_messages()` gains `sensory_hints` optional param

## Test Files
- tests/test_environment_tod.py — 10 tests (E-20)
- tests/test_environment_sensory.py — 8 tests (E-21)
- tests/test_environment_objects.py — 12 tests (E-22)

## Resume Procedure
Read this file + ENHANCEMENT_PLAN.md Wave 5 section + environment_mapper.py
