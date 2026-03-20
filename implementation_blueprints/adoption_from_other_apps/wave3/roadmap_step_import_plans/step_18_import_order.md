# Roadmap Step 18 Import Plan

## Import Order
- 1. `code_of_other_apps_that_can_be_adopted/turn_processor.py` - Prompt assembly pipeline shape.
- 2. `code_of_other_apps_that_can_be_adopted/enhanced_context_builder.py` - Context sectioning and ordering approach.
- 3. `code_of_other_apps_that_can_be_adopted/local_providers.py` - Provider call surface pattern.

## Adapter Notes
- Keep imports behind adapter boundaries in target modules.
- Preserve deterministic behavior and typed outputs.
- Remove game-specific assumptions during adaptation.

## Validation Gate
- Unit coverage for imported logic paths.
- Integration coverage against state bus and prompt contracts.
- Security and logging checks pass before enabling by default.