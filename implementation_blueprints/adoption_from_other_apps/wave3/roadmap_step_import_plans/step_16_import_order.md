# Roadmap Step 16 Import Plan

## Import Order
- 1. `code_of_other_apps_that_can_be_adopted/story_phase.py` - Project lifecycle phase patterns.
- 2. `code_of_other_apps_that_can_be_adopted/world_will.py` - Goal pressure modulation ideas.

## Adapter Notes
- Keep imports behind adapter boundaries in target modules.
- Preserve deterministic behavior and typed outputs.
- Remove game-specific assumptions during adaptation.

## Validation Gate
- Unit coverage for imported logic paths.
- Integration coverage against state bus and prompt contracts.
- Security and logging checks pass before enabling by default.