# Import Risk - memory_system.py

## Source
- `code_of_other_apps_that_can_be_adopted/memory_system.py`

## Primary Risk
- Context bloat and stale summary drift.

## Mitigation
- Cap context windows and nightly compaction.

## Required Test
- Add at least one failing regression case then verify fix.
- Verify behavior in degraded/fallback mode.
