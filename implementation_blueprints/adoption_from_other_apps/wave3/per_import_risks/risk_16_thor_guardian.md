# Import Risk - thor_guardian.py

## Source
- `code_of_other_apps_that_can_be_adopted/thor_guardian.py`

## Primary Risk
- Circuit opens too aggressively.

## Mitigation
- Per-operation thresholds and cooldown tuning.

## Required Test
- Add at least one failing regression case then verify fix.
- Verify behavior in degraded/fallback mode.
