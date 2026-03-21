# Adoption Card - data_system.py

## Source
- `code_of_other_apps_that_can_be_adopted/data_system.py`

## Why It Matters
- Foundational multi-format loader.

## Roadmap Mapping
- Steps: 5,13,17

## Copy/Adapt Guidance
- Copy loader core; adapt paths/schemas.

## Pre-Import Checks
- Verify imports do not require missing game-only modules
- Verify file IO is sandboxed to project runtime directories
- Verify config keys map to current data files

## Test Focus
- Deterministic unit tests
- State-bus integration tests
- Failure-path degradation tests
