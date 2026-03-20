# Roadmap Step 20 Import Plan

## Import Order
- 1. `code_of_other_apps_that_can_be_adopted/comprehensive_logging.py` - Calibration signal extraction from logs.
- 2. `code_of_other_apps_that_can_be_adopted/timeline_service.py` - Stable baseline timing for comparisons.

## Adapter Notes
- Keep imports behind adapter boundaries in target modules.
- Preserve deterministic behavior and typed outputs.
- Remove game-specific assumptions during adaptation.

## Validation Gate
- Unit coverage for imported logic paths.
- Integration coverage against state bus and prompt contracts.
- Security and logging checks pass before enabling by default.