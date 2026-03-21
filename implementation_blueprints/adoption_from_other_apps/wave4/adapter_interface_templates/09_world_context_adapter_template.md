# Adapter Interface Template - 09 World Context Adapter

## Mapping
- world_systems.py + timeline_service.py to environment mapper

## Required Functions
- resolve_location(), resolve_time_segment(), export_environment_context()

## Output Payloads
- EnvironmentContextPayload

## Rules
- Keep adapter thin; keep business logic in imported module core.
- Validate and normalize all outputs before publish.
- Emit correlation IDs on every adapter event.
