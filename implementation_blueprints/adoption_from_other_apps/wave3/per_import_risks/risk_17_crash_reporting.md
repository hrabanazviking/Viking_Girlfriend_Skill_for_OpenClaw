# Import Risk - crash_reporting.py

## Source
- `code_of_other_apps_that_can_be_adopted/crash_reporting.py`

## Primary Risk
- PII leakage in exception metadata.

## Mitigation
- Redaction pass before log persistence.

## Required Test
- Add at least one failing regression case then verify fix.
- Verify behavior in degraded/fallback mode.
