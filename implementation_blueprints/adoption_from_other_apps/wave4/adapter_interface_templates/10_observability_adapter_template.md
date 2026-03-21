# Adapter Interface Template - 10 Observability Adapter

## Mapping
- comprehensive_logging.py + crash_reporting.py to observability stack

## Required Functions
- log_cycle_event(), log_ai_call(), report_incident()

## Output Payloads
- LogEventPayload, IncidentPayload

## Rules
- Keep adapter thin; keep business logic in imported module core.
- Validate and normalize all outputs before publish.
- Emit correlation IDs on every adapter event.
