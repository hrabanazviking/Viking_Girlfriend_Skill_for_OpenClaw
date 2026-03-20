# Roadmap Step 03 Import Plan

## Import Order
- 1. `code_of_other_apps_that_can_be_adopted/local_providers.py` - Model listing/health hooks for local runtime.
- 2. `code_of_other_apps_that_can_be_adopted/thor_guardian.py` - Guard provisioning operations with retries/circuit breaker.

## Adapter Notes
- Keep imports behind adapter boundaries in target modules.
- Preserve deterministic behavior and typed outputs.
- Remove game-specific assumptions during adaptation.

## Validation Gate
- Unit coverage for imported logic paths.
- Integration coverage against state bus and prompt contracts.
- Security and logging checks pass before enabling by default.