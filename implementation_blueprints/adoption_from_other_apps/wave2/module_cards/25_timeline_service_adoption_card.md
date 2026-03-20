# Adoption Card - timeline_service.py

## Source
- `code_of_other_apps_that_can_be_adopted/timeline_service.py`

## Why It Matters
- Deterministic timeline service.

## Roadmap Mapping
- Steps: 15,17

## Copy/Adapt Guidance
- Copy clock logic; adapt life-context segments.

## Pre-Import Checks
- Verify imports do not require missing game-only modules
- Verify file IO is sandboxed to project runtime directories
- Verify config keys map to current data files

## Test Focus
- Deterministic unit tests
- State-bus integration tests
- Failure-path degradation tests
