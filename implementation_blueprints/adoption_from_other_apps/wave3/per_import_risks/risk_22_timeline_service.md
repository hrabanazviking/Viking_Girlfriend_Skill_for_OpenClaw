# Import Risk - timeline_service.py

## Source
- `code_of_other_apps_that_can_be_adopted/timeline_service.py`

## Primary Risk
- Timeline drift after restarts.

## Mitigation
- Persist canonical clock state each cycle.

## Required Test
- Add at least one failing regression case then verify fix.
- Verify behavior in degraded/fallback mode.
