# Implementation File Order - 01 Foundation

## Build Order
- 1. `scripts/config_loader.py`
- 2. `scripts/state_bus.py`
- 3. `scripts/runtime_kernel.py`
- 4. `scripts/observability_stack.py`
- 5. `scripts/security.py`

## Gate Before Next File
- Current file has tests and contract checks.
- Logging and error paths are wired.
- No unresolved TODO or orphan integration points.
