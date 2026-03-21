# Adoption Card - local_providers.py

## Source
- `code_of_other_apps_that_can_be_adopted/local_providers.py`

## Why It Matters
- Local model provider abstraction.

## Roadmap Mapping
- Steps: 2,3,18

## Copy/Adapt Guidance
- Copy client abstraction; adapt LiteLLM routing intents.

## Pre-Import Checks
- Verify imports do not require missing game-only modules
- Verify file IO is sandboxed to project runtime directories
- Verify config keys map to current data files

## Test Focus
- Deterministic unit tests
- State-bus integration tests
- Failure-path degradation tests
