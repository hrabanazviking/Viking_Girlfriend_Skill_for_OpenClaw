# Adoption Card - voice_bridge.py

## Source
- `code_of_other_apps_that_can_be_adopted/voice_bridge.py`

## Why It Matters
- Defensive STT/TTS bridge.

## Roadmap Mapping
- Steps: optional

## Copy/Adapt Guidance
- Copy resilience patterns; feature-flag voice stack.

## Pre-Import Checks
- Verify imports do not require missing game-only modules
- Verify file IO is sandboxed to project runtime directories
- Verify config keys map to current data files

## Test Focus
- Deterministic unit tests
- State-bus integration tests
- Failure-path degradation tests
