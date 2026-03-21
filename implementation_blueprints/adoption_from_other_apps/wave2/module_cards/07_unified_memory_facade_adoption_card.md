# Adoption Card - unified_memory_facade.py

## Source
- `code_of_other_apps_that_can_be_adopted/unified_memory_facade.py`

## Why It Matters
- Facade over memory backends.

## Roadmap Mapping
- Steps: 13,18

## Copy/Adapt Guidance
- Copy facade pattern; adapt contracts.

## Pre-Import Checks
- Verify imports do not require missing game-only modules
- Verify file IO is sandboxed to project runtime directories
- Verify config keys map to current data files

## Test Focus
- Deterministic unit tests
- State-bus integration tests
- Failure-path degradation tests
