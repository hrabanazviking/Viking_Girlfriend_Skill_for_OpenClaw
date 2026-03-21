# Import Risk - rag_system.py

## Source
- `code_of_other_apps_that_can_be_adopted/rag_system.py`

## Primary Risk
- Retrieval irrelevance on mixed datasets.

## Mitigation
- Hybrid scoring and domain filters.

## Required Test
- Add at least one failing regression case then verify fix.
- Verify behavior in degraded/fallback mode.
