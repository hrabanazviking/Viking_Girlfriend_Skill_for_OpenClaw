# Import Risk - data_system.py

## Source
- `code_of_other_apps_that_can_be_adopted/data_system.py`

## Primary Risk
- Schema mismatch across YAML/JSON variants.

## Mitigation
- Enforce schema validators at loader boundary.

## Required Test
- Add at least one failing regression case then verify fix.
- Verify behavior in degraded/fallback mode.
