# Module Spec - bio_engine

## Mission
Track cycle phase, biorhythms, energy baseline, and libido drift factors.

## Responsibilities
- Provide a stable API boundary for this capability
- Isolate business logic from transport/framework details
- Publish normalized outputs to the shared state bus

## Internal Components
- `schema`: typed config and runtime model definitions
- `core`: deterministic pure logic
- `adapter`: IO integrations and framework bindings
- `tests`: unit and contract tests for all public interfaces

## Inputs
- Runtime clock and scheduler triggers
- User message context and conversation metadata
- Data files in `viking_girlfriend_skill/data`

## Outputs
- Typed state payloads for prompt synthesis
- Structured telemetry events
- Recoverable errors with remediation hints

## Failure Modes
- Missing/invalid config -> fail fast with actionable validation error
- External dependency timeout -> fallback state and degraded mode flag
- Inconsistent state transitions -> quarantine event and force re-sync

## Milestones
- M1: interface design and fixtures
- M2: core logic + edge-case unit tests
- M3: adapter integration + logging
- M4: contract tests against prompt synthesizer expectations
