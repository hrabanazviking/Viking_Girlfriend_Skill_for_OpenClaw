# Dependency Graph - 03 Security Cluster

## Primary Modules
- thor_guardian.py, crash_reporting.py, social_protocol_engine.py, memory_hardening.py

## Inbound Dependencies
- Runtime orchestrator and command gateway

## Outbound Contracts
- Guarded execution results, policy deny events

## Integration Rules
- Keep module boundaries explicit and adapter-driven.
- No direct cross-cluster state mutation.
- Publish typed payloads on the state/event bus only.
