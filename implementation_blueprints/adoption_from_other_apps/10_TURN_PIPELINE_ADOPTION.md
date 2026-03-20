# Turn Pipeline Adoption

## Source Module
- `code_of_other_apps_that_can_be_adopted/turn_processor.py`

## Roadmap Fit
- Step 5 (main loop)
- Step 15 (scheduler and activity execution)
- Step 18 (prompt synthesis)

## Reusable Pieces
- Central coordinator pattern for assembling context.
- Response post-processing hooks.
- Quest/event extraction style as generic parser pattern.

## Required Adaptations
- Replace game turn context with OpenClaw message/task context.
- Strip combat/quest assumptions.
- Wire to scheduler activities and trust/security middleware.

## Acceptance Criteria
- One orchestrator drives pre-process, model call, post-process, persistence.
- Orchestrator failures return safe degraded response paths.
- Unit tests cover context build and response extraction boundaries.
