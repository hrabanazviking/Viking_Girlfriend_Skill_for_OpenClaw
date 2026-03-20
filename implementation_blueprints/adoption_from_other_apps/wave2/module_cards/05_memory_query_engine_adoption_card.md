# Adoption Card - memory_query_engine.py

## Source
- `code_of_other_apps_that_can_be_adopted/memory_query_engine.py`

## Why It Matters
- Structured memory query surface.

## Roadmap Mapping
- Steps: 13,18

## Copy/Adapt Guidance
- Copy query model; adapt trust filters.

## Pre-Import Checks
- Verify imports do not require missing game-only modules
- Verify file IO is sandboxed to project runtime directories
- Verify config keys map to current data files

## Test Focus
- Deterministic unit tests
- State-bus integration tests
- Failure-path degradation tests
