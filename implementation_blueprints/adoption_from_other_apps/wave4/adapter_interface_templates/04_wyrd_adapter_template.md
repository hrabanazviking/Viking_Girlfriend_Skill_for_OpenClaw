# Adapter Interface Template - 04 Wyrd Adapter

## Mapping
- wyrd_system.py + world_will.py to oracle runtime

## Required Functions
- ingest_turn(), derive_daily_oracle(), export_wyrd_state()

## Output Payloads
- WyrdStatePayload, OraclePayload

## Rules
- Keep adapter thin; keep business logic in imported module core.
- Validate and normalize all outputs before publish.
- Emit correlation IDs on every adapter event.
