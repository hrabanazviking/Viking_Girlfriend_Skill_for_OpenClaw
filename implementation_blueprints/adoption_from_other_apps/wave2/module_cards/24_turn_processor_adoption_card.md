# Adoption Card - turn_processor.py

## Source
- `code_of_other_apps_that_can_be_adopted/turn_processor.py`

## Why It Matters
- Central orchestration pipeline shell.

## Roadmap Mapping
- Steps: 5,15,18

## Copy/Adapt Guidance
- Copy orchestration shape; strip RPG assumptions.

## Pre-Import Checks
- Verify imports do not require missing game-only modules
- Verify file IO is sandboxed to project runtime directories
- Verify config keys map to current data files

## Test Focus
- Deterministic unit tests
- State-bus integration tests
- Failure-path degradation tests
