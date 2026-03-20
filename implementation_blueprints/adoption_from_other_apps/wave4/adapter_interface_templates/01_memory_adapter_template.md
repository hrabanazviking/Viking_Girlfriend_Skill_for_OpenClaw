# Adapter Interface Template - 01 Memory Adapter

## Mapping
- Memory modules to runtime memory manager

## Required Functions
- ingest_event(), summarize_window(), retrieve_context()

## Output Payloads
- MemoryStatePayload, RetrievalPayload

## Rules
- Keep adapter thin; keep business logic in imported module core.
- Validate and normalize all outputs before publish.
- Emit correlation IDs on every adapter event.
