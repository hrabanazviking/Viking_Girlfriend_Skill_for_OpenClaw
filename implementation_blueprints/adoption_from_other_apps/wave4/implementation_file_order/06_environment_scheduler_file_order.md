# Implementation File Order - 06 Environment Scheduler

## Build Order
- 1. `scripts/environment_context.py`
- 2. `scripts/scheduler.py`
- 3. `scripts/activity_runtime.py`
- 4. `scripts/project_generator.py`

## Gate Before Next File
- Current file has tests and contract checks.
- Logging and error paths are wired.
- No unresolved TODO or orphan integration points.
