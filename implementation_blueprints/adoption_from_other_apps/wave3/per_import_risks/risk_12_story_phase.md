# Import Risk - story_phase.py

## Source
- `code_of_other_apps_that_can_be_adopted/story_phase.py`

## Primary Risk
- Phase progression disconnected from outcomes.

## Mitigation
- Gate transitions on explicit completion metrics.

## Required Test
- Add at least one failing regression case then verify fix.
- Verify behavior in degraded/fallback mode.
