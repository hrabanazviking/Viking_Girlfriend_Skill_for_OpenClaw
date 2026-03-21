# Roadmap Step 08 Import Plan

## Import Order
- 1. `code_of_other_apps_that_can_be_adopted/wyrd_system.py` - Primary fate/oracle state model.
- 2. `code_of_other_apps_that_can_be_adopted/world_will.py` - Ambient intent context layer.
- 3. `code_of_other_apps_that_can_be_adopted/story_phase.py` - Long-arc thematic phase support.

## Adapter Notes
- Keep imports behind adapter boundaries in target modules.
- Preserve deterministic behavior and typed outputs.
- Remove game-specific assumptions during adaptation.

## Validation Gate
- Unit coverage for imported logic paths.
- Integration coverage against state bus and prompt contracts.
- Security and logging checks pass before enabling by default.