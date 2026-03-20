# Dependency Graph - 02 State Cluster

## Primary Modules
- menstrual_cycle.py, emotional_engine.py, stress_system.py, wyrd_system.py, world_will.py, story_phase.py

## Inbound Dependencies
- Timeline service, environment context

## Outbound Contracts
- Bio state, PAD signals, oracle state

## Integration Rules
- Keep module boundaries explicit and adapter-driven.
- No direct cross-cluster state mutation.
- Publish typed payloads on the state/event bus only.
