# Roadmap Step 11 Import Plan

## Import Order
- 1. `code_of_other_apps_that_can_be_adopted/social_ledger.py` - Evidence ledger pattern for trust updates.
- 2. `code_of_other_apps_that_can_be_adopted/relationship_graph.py` - Scoring transforms for trust shifts.

## Adapter Notes
- Keep imports behind adapter boundaries in target modules.
- Preserve deterministic behavior and typed outputs.
- Remove game-specific assumptions during adaptation.

## Validation Gate
- Unit coverage for imported logic paths.
- Integration coverage against state bus and prompt contracts.
- Security and logging checks pass before enabling by default.