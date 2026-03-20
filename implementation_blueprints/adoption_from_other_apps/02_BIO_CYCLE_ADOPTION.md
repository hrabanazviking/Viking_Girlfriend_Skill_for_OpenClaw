# Bio Cycle Adoption

## Source Module
- `code_of_other_apps_that_can_be_adopted/menstrual_cycle.py`

## Roadmap Fit
- Step 7 (bio-cyclical engine)
- Step 6 (PAD input source)

## Reusable Pieces
- Multi-phase cycle definitions and fallback table design.
- Per-phase emotion multipliers and behavior-bias fields.
- Turn tick model for cycle progression.

## Required Adaptations
- Map cycle phases into `scripts/bio_engine.py` state contract.
- Remove game-specific prompt hooks and replace with OpenClaw state bus output.
- Bind phase outputs to Wyrd PAD coefficients, not direct narrative text.

## Acceptance Criteria
- Deterministic cycle phase for any timestamp and seed.
- Output includes phase name, energy modifier, emotion multipliers.
- Unit tests validate phase boundaries and rollover behavior.
