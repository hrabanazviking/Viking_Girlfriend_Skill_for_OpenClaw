# Adapter Interface Template - 02 Bio Adapter

## Mapping
- menstrual_cycle.py to bio_engine runtime

## Required Functions
- compute_phase(), compute_modifiers(), export_bio_state()

## Output Payloads
- BioStatePayload

## Rules
- Keep adapter thin; keep business logic in imported module core.
- Validate and normalize all outputs before publish.
- Emit correlation IDs on every adapter event.
