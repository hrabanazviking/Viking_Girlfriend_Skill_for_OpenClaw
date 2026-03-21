# Dependency Graph - 06 Observability Cluster

## Primary Modules
- comprehensive_logging.py, crash_reporting.py, timeline_service.py

## Inbound Dependencies
- All runtime modules

## Outbound Contracts
- Structured logs, incident reports, calibration metrics

## Integration Rules
- Keep module boundaries explicit and adapter-driven.
- No direct cross-cluster state mutation.
- Publish typed payloads on the state/event bus only.
