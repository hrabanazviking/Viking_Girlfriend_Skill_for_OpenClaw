# Adapter Interface Template - 06 Trust Adapter

## Mapping
- social_ledger.py + relationship_graph.py to trust engine

## Required Functions
- ingest_evidence(), recompute_tier(), export_trust_state()

## Output Payloads
- TrustStatePayload

## Rules
- Keep adapter thin; keep business logic in imported module core.
- Validate and normalize all outputs before publish.
- Emit correlation IDs on every adapter event.
