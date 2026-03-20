# Integration Contract - router_contract

## Scope
LiteLLM request/response schema and retry policy by route.

## Producers
- Modules that emit this artifact

## Consumers
- Modules and tests that depend on this artifact

## Schema (Draft)
- version: semantic schema version string
- timestamp: ISO-8601 UTC
- source: module identifier
- payload: typed object validated before publish

## Validation Rules
- Reject unknown required fields
- Preserve backward compatibility for one minor version
- Emit migration notices when schema changes

## Test Strategy
- Golden fixtures for happy path
- Fuzzed malformed payloads
- Compatibility tests across two schema versions
