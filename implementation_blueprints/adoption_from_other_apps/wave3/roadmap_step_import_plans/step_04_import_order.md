# Roadmap Step 04 Import Plan

## Import Order
- 1. `code_of_other_apps_that_can_be_adopted/turn_processor.py` - Use orchestration skeleton for skill registration flow.

## Adapter Notes
- Keep imports behind adapter boundaries in target modules.
- Preserve deterministic behavior and typed outputs.
- Remove game-specific assumptions during adaptation.

## Validation Gate
- Unit coverage for imported logic paths.
- Integration coverage against state bus and prompt contracts.
- Security and logging checks pass before enabling by default.