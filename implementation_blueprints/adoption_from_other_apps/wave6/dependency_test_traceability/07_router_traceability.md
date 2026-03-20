# Dependency Test Traceability - 07 Router

## Source Dependencies
- local_providers.py, openrouter.py

## Required Test Suites
- unit_router_failover, integration_prompt_to_router, e2e_model_routing_cycle

## Roadmap Coverage
- step_02, step_03, step_18

## Pass Conditions
- Unit tests are deterministic with seeded fixtures.
- Integration tests validate schema contracts.
- E2E tests validate degraded/fallback behavior.
