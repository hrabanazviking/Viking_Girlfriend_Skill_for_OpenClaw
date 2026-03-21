# Dependency Test Traceability - 08 Orchestrator

## Source Dependencies
- turn_processor.py, timeline_service.py

## Required Test Suites
- unit_cycle_orchestrator, integration_cycle_pipeline, e2e_restart_recovery_cycle

## Roadmap Coverage
- step_05, step_15, step_20

## Pass Conditions
- Unit tests are deterministic with seeded fixtures.
- Integration tests validate schema contracts.
- E2E tests validate degraded/fallback behavior.
