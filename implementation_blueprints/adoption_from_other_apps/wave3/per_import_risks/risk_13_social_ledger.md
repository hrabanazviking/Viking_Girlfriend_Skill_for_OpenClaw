# Import Risk - social_ledger.py

## Source
- `code_of_other_apps_that_can_be_adopted/social_ledger.py`

## Primary Risk
- Trust evidence skew from keyword heuristics.

## Mitigation
- Weighted evidence with manual override hooks.

## Required Test
- Add at least one failing regression case then verify fix.
- Verify behavior in degraded/fallback mode.
