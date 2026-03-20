# Adapter Interface Template - 07 Router Adapter

## Mapping
- local_providers.py/openrouter.py to model router

## Required Functions
- route_request(), fallback_route(), export_route_metrics()

## Output Payloads
- RouteResultPayload

## Rules
- Keep adapter thin; keep business logic in imported module core.
- Validate and normalize all outputs before publish.
- Emit correlation IDs on every adapter event.
