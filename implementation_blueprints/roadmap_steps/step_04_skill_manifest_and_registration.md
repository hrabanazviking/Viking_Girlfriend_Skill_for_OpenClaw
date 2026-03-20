# Step 04 Blueprint - Skill manifest and registration

## Objective
Implement roadmap step 4 as a production-capable module with deterministic behavior and clear observability.

## Primary Target
- Planned file: `skill/manifest_builder.py`
- Upstream dependencies: previous roadmap steps that produce state/config needed by this step
- Downstream dependencies: prompt synthesis, testing, and launch calibration

## Build Plan
- SKILL.md validator, entrypoint checks, OpenClaw discovery hooks
- Define typed interfaces first, then implement pure functions before side-effecting adapters
- Add unit tests for edge conditions and failure paths

## Data Inputs
- `README.md` architectural intent and feature scope
- `ROADMAP.md` step-specific deliverables
- `viking_girlfriend_skill/data/*` identity, values, environment, and security policy files

## API Contract (Draft)
- Input: normalized runtime context object and step-local config
- Output: deterministic state object plus optional events/alerts
- Error model: typed recoverable errors and explicit hard-fail exceptions

## Verification Checklist
- Functional behavior matches roadmap deliverable: Skill appears in OpenClaw UI
- Logging includes stable event names and correlation IDs
- Failure modes are tested with graceful degradation where possible

## Implementation Notes
- Prefer pure computation core + thin IO wrapper architecture
- Keep all constants in explicit config schemas to simplify calibration
- Emit artifacts needed by step 19 integration tests
