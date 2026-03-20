# World Context Adoption

## Source Modules
- `code_of_other_apps_that_can_be_adopted/world_systems.py`
- `code_of_other_apps_that_can_be_adopted/timeline_service.py`
- `code_of_other_apps_that_can_be_adopted/world_loom.py`

## Roadmap Fit
- Step 15 (activity scheduler)
- Step 17 (environment mapping)
- Step 18 (prompt context)

## Reusable Pieces
- Structured location/party/faction state models.
- Deterministic timeline progression logic.
- World context block generation patterns.

## Required Adaptations
- Map city-grid concepts into `environment.json` locations and third places.
- Keep only needed context dimensions: location, time segment, active activity.
- Ensure no heavy RPG mechanics leak into companion runtime.

## Acceptance Criteria
- Location transitions remain coherent over long sessions.
- Time context is deterministic across restarts.
- Prompt receives compact, stable world-context section.
