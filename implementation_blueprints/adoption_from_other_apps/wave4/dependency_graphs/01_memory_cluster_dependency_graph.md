# Dependency Graph - 01 Memory Cluster

## Primary Modules
- memory_system.py, enhanced_memory.py, character_memory_rag.py, memory_query_engine.py, memory_hardening.py, unified_memory_facade.py

## Inbound Dependencies
- Data loader, trust filter, prompt synthesizer

## Outbound Contracts
- Memory API, summary output, retrieval payloads

## Integration Rules
- Keep module boundaries explicit and adapter-driven.
- No direct cross-cluster state mutation.
- Publish typed payloads on the state/event bus only.
