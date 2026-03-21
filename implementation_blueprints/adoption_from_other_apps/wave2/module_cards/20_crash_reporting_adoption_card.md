# Adoption Card - crash_reporting.py

## Source
- `code_of_other_apps_that_can_be_adopted/crash_reporting.py`

## Why It Matters
- Structured incident reporting.

## Roadmap Mapping
- Steps: 10,19

## Copy/Adapt Guidance
- Copy report envelope; adapt storage policy.

## Pre-Import Checks
- Verify imports do not require missing game-only modules
- Verify file IO is sandboxed to project runtime directories
- Verify config keys map to current data files

## Test Focus
- Deterministic unit tests
- State-bus integration tests
- Failure-path degradation tests
