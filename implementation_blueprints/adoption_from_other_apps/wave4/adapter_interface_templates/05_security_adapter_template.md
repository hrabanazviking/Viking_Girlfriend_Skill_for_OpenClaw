# Adapter Interface Template - 05 Security Adapter

## Mapping
- thor_guardian.py + protocol checks to security sentinel

## Required Functions
- guard_call(), classify_risk(), emit_security_event()

## Output Payloads
- SecurityDecisionPayload

## Rules
- Keep adapter thin; keep business logic in imported module core.
- Validate and normalize all outputs before publish.
- Emit correlation IDs on every adapter event.
