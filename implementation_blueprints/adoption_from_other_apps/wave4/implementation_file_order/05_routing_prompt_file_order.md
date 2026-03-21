# Implementation File Order - 05 Routing Prompt

## Build Order
- 1. `scripts/prompt_synthesizer.py`
- 2. `scripts/model_router.py`
- 3. `scripts/provider_clients.py`
- 4. `scripts/response_postprocess.py`

## Gate Before Next File
- Current file has tests and contract checks.
- Logging and error paths are wired.
- No unresolved TODO or orphan integration points.
