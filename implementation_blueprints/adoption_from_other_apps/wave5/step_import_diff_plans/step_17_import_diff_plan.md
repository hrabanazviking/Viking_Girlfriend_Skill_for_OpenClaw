# Step 17 Import Diff Plan

## Source Modules
- `code_of_other_apps_that_can_be_adopted/world_systems.py`
- `code_of_other_apps_that_can_be_adopted/timeline_service.py`

## Target File Touch Order
- `scripts/*` adapter file first
- `scripts/*` state contract update second
- `tests/*` unit coverage third
- `tests/*` integration coverage fourth

## Required Diff Shape
- Additive imports only; no broad refactors during first adoption pass.
- Keep imported behavior behind explicit adapter boundaries.
- Preserve existing APIs while adding new optional fields.

## Verification
- Contract payload validates against current schema docs.
- Fallback/degraded mode path is reachable and tested.
- No hardcoded data/settings introduced.
