# Adapter Interface Template - 03 Emotion Adapter

## Mapping
- emotional_engine.py + stress_system.py to wyrd matrix

## Required Functions
- apply_stimulus(), decay_state(), export_affect_signals()

## Output Payloads
- AffectSignalPayload, StressEventPayload

## Rules
- Keep adapter thin; keep business logic in imported module core.
- Validate and normalize all outputs before publish.
- Emit correlation IDs on every adapter event.
