# Roadmap Step 06 Import Plan

## Import Order
- 1. `code_of_other_apps_that_can_be_adopted/emotional_engine.py` - Signal engine for PAD inputs.
- 2. `code_of_other_apps_that_can_be_adopted/stress_system.py` - Threshold events feeding PAD dominance.
- 3. `code_of_other_apps_that_can_be_adopted/personality_engine.py` - Behavior modulation overlays.

## Adapter Notes
- Keep imports behind adapter boundaries in target modules.
- Preserve deterministic behavior and typed outputs.
- Remove game-specific assumptions during adaptation.

## Validation Gate
- Unit coverage for imported logic paths.
- Integration coverage against state bus and prompt contracts.
- Security and logging checks pass before enabling by default.