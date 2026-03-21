# Router And Provider Adoption

## Source Modules
- `code_of_other_apps_that_can_be_adopted/local_providers.py`
- `code_of_other_apps_that_can_be_adopted/openrouter.py`

## Roadmap Fit
- Step 2 (service integration)
- Step 3 (local model worker)
- Step 18 (prompt to model routing)

## Reusable Pieces
- Provider client abstraction for local OpenAI-compatible endpoints.
- Model fallback and recommendation metadata patterns.
- Client-side timeout/retry behavior.

## Required Adaptations
- Replace direct provider routing with LiteLLM-compatible intent layer.
- Use environment-based secrets only; remove inline key assumptions.
- Keep OpenRouter optional behind explicit configuration.

## Acceptance Criteria
- Router client can target conscious/deep/subconscious lanes.
- Failure in one provider lane does not crash message pipeline.
- Provider selection and fallback emit structured telemetry events.
