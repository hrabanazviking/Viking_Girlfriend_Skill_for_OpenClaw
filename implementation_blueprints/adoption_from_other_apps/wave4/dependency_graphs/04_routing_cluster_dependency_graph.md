# Dependency Graph - 04 Routing Cluster

## Primary Modules
- local_providers.py, openrouter.py, turn_processor.py

## Inbound Dependencies
- Prompt synthesis and trust/security gates

## Outbound Contracts
- Model response payload, route telemetry

## Integration Rules
- Keep module boundaries explicit and adapter-driven.
- No direct cross-cluster state mutation.
- Publish typed payloads on the state/event bus only.
