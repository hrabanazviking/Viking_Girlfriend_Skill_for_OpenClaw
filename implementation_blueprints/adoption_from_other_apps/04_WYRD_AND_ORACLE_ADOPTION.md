# Wyrd And Oracle Adoption

## Source Modules
- `code_of_other_apps_that_can_be_adopted/wyrd_system.py`
- `code_of_other_apps_that_can_be_adopted/wyrd_tethers.py`
- `code_of_other_apps_that_can_be_adopted/world_will.py`
- `code_of_other_apps_that_can_be_adopted/story_phase.py`
- `code_of_other_apps_that_can_be_adopted/world_dreams.py`

## Roadmap Fit
- Step 8 (abstract variance core)
- Step 18 (prompt synthesis flavor/context)

## Reusable Pieces
- Three-wells structural model (past/present/future partitions).
- Turn summary ingestion and fate-thread persistence patterns.
- World-will atmosphere block generation.

## Required Adaptations
- Convert narrative-heavy fields into lightweight structured state.
- Bind daily deterministic seeding to calendar + user/session seed.
- Route dream outputs to nocturnal pipeline only (not live-response path).

## Acceptance Criteria
- Daily oracle output is reproducible and explainable.
- Wyrd state yields compact prompt payload with bounded token budget.
- Prophecy/fate thread persistence survives restart.
