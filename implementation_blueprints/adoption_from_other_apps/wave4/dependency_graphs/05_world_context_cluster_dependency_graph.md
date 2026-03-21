# Dependency Graph - 05 World Context Cluster

## Primary Modules
- world_systems.py, timeline_service.py, witch_system.py, rag_system.py

## Inbound Dependencies
- Data loader and memory index

## Outbound Contracts
- Location context, lore context blocks

## Integration Rules
- Keep module boundaries explicit and adapter-driven.
- No direct cross-cluster state mutation.
- Publish typed payloads on the state/event bus only.
