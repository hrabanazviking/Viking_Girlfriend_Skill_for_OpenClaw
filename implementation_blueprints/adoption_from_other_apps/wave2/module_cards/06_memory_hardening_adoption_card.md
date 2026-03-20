# Adoption Card - memory_hardening.py

## Source
- `code_of_other_apps_that_can_be_adopted/memory_hardening.py`

## Why It Matters
- Memory drift and context hardening.

## Roadmap Mapping
- Steps: 12,18

## Copy/Adapt Guidance
- Copy guard logic; adapt refusal paths.

## Pre-Import Checks
- Verify imports do not require missing game-only modules
- Verify file IO is sandboxed to project runtime directories
- Verify config keys map to current data files

## Test Focus
- Deterministic unit tests
- State-bus integration tests
- Failure-path degradation tests
