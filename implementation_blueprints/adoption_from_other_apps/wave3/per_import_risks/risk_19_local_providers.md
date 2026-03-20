# Import Risk - local_providers.py

## Source
- `code_of_other_apps_that_can_be_adopted/local_providers.py`

## Primary Risk
- Provider timeout cascades.

## Mitigation
- Strict timeouts and fallback lanes.

## Required Test
- Add at least one failing regression case then verify fix.
- Verify behavior in degraded/fallback mode.
