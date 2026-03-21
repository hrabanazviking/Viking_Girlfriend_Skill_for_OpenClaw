# Import Risk - social_protocol_engine.py

## Source
- `code_of_other_apps_that_can_be_adopted/social_protocol_engine.py`

## Primary Risk
- False positives in compliance gating.

## Mitigation
- Human-readable reason codes and retry path.

## Required Test
- Add at least one failing regression case then verify fix.
- Verify behavior in degraded/fallback mode.
