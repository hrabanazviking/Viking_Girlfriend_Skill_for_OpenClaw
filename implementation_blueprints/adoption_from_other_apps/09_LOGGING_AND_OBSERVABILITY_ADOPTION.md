# Logging And Observability Adoption

## Source Module
- `code_of_other_apps_that_can_be_adopted/comprehensive_logging.py`

## Roadmap Fit
- Step 5 (runtime foundation)
- Step 19 (end-to-end testing)
- Step 20 (launch calibration)

## Reusable Pieces
- Turn-level log envelope.
- AI-call logging with prompt/response metadata.
- Data-path and state-change event logging helpers.

## Required Adaptations
- Remove game turn language and convert to interaction-cycle naming.
- Add correlation IDs and schema version tags to every event.
- Redact sensitive data before persistence.

## Acceptance Criteria
- Every response cycle emits start/end events with durations.
- Failures capture stack trace plus module identifier.
- Session summary can be generated without parsing raw logs manually.
