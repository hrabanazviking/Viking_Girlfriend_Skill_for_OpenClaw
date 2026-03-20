# Adapter Interface Template - 08 Orchestrator Adapter

## Mapping
- turn_processor.py to runtime kernel

## Required Functions
- build_cycle_context(), run_cycle(), persist_cycle_artifacts()

## Output Payloads
- CycleResultPayload

## Rules
- Keep adapter thin; keep business logic in imported module core.
- Validate and normalize all outputs before publish.
- Emit correlation IDs on every adapter event.
