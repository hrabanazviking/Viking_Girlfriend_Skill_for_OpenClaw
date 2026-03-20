# Implementation File Order - 07 Test And Launch

## Build Order
- 1. `tests/test_unit_state.py`
- 2. `tests/test_integration_pipelines.py`
- 3. `tests/test_e2e_system.py`
- 4. `ops/launch_calibration.py`
- 5. `ops/autostart_setup.py`

## Gate Before Next File
- Current file has tests and contract checks.
- Logging and error paths are wired.
- No unresolved TODO or orphan integration points.
