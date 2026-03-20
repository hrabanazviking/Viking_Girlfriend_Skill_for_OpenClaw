# Adoption Card - comprehensive_logging.py

## Source
- `code_of_other_apps_that_can_be_adopted/comprehensive_logging.py`

## Why It Matters
- Rich per-cycle logging model.

## Roadmap Mapping
- Steps: 5,19,20

## Copy/Adapt Guidance
- Copy log envelope; adapt naming and redaction.

## Pre-Import Checks
- Verify imports do not require missing game-only modules
- Verify file IO is sandboxed to project runtime directories
- Verify config keys map to current data files

## Test Focus
- Deterministic unit tests
- State-bus integration tests
- Failure-path degradation tests
