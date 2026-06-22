# Comprehensive Bug Report and Analysis

**Date:** 2026-04-24

## 1. Overview
A comprehensive scan of the `viking_girlfriend_skill` codebase was conducted using Flake8, PyLint, Bandit, Mypy, and Pytest. The following document outlines the discovered bugs, categorized by severity and domain, along with research context and recommended code changes.

## 2. Issues Discovered

### 2.1 Concurrency and Asynchronous Execution Bugs

**Error Code:** `[unused-coroutine]` (Mypy)
**Files Affected:**
- `trust_engine.py` (Lines 588, 764)
- `security.py` (Line 508)
- `scheduler.py` (Line 436)
- `project_generator.py` (Line 231)
- `ethics.py` (Line 490)
- `dream_engine.py` (Line 387)
- `environment_mapper.py` (Line 267)
- `model_router_client.py` (Line 1267)
- `prompt_synthesizer.py` (Lines 430, 740, 907)
- `memory_store.py` (Line 1006)

**Context and Research:**
Based on standard Python `asyncio` rules (ref: `https://docs.python.org/3/library/asyncio-task.html`), calling an `async def` function creates a coroutine object but *does not execute it*. The coroutine must be `await`ed, or scheduled via `asyncio.create_task()`.
According to `mypy` documentation for `unused-coroutine` (ref: `https://mypy.readthedocs.io/en/stable/error_code_list.html#check-that-coroutine-return-value-is-used-unused-coroutine`), "Mypy ensures that return values of async def functions are not ignored, as this is usually a programming error, as the coroutine won’t be executed at the call site."

**Recommended Code Change:**
Locate the un-awaited calls in the specified lines and insert `await ` before the function call if it's within an async context. If the intention is to run it concurrently without blocking, wrap it in `asyncio.create_task(func())`.

---

### 2.2 Typing and Assignment Errors

**Error Code:** `[assignment]` and `[attr-defined]` (Mypy)
**Files Affected:**
- `security.py` (Line 612): `Incompatible types in assignment (expression has type "frozenset[str]", variable has type "set[str]")`
- `vordur.py` (Lines 687, 1298, 1881): `Item "None" of "Any | None" has no attribute "complete"`
- `vordur.py` (Line 774): `Module "scripts.mimir_well" has no attribute "VerdictLabel"`
- `main.py` (Lines 511-530): Multiple incorrect assignments to a `WyrdState` variable (assigned `BioState`, `DreamState`, `OracleState` which lack corresponding attributes).
- `cove_pipeline.py` (Line 364): `Name "draft" already defined on line 318 [no-redef]`

**Context and Research:**
Python type hints enforce static assignment rules.
- `frozenset` vs `set`: A `frozenset` is immutable while `set` is mutable. If a variable is typed as `set[str]`, assigning a `frozenset` violates the typing contract because the system assumes the set can be modified (e.g. `.add()`).
- `Any | None`: Represents an optional value. Accessing an attribute (like `.complete`) on an object that could be `None` is unsafe and triggers `[union-attr]`.
- Re-definitions: Defining a variable like `draft` twice in the same scope with different types violates Mypy's single-definition rule `[no-redef]`.

**Recommended Code Change:**
- `security.py`: Cast or convert the frozenset using `set(the_frozenset)`.
- `vordur.py`: Wrap the attribute access in a `None` check (e.g., `if obj is not None: obj.complete`). Verify `VerdictLabel` import from `mimir_well.py` (it might have been renamed or removed).
- `main.py`: Refactor variable naming so that distinct variables are used for distinct state types (e.g., `bio_state = ...`, `dream_state = ...`) rather than reusing a single `WyrdState` variable.
- `cove_pipeline.py`: Rename the second instance of `draft` to something like `final_draft`.

---

### 2.3 Dependency and Environment Issues

**Error Code:** `[import-untyped]` and `[import-not-found]` (Mypy)
**Files Affected:**
- Missing `yaml` stubs in `config_loader.py`, `oracle.py`, `bio_engine.py`, `mimir_well.py`.
- Missing `psutil` stubs in `metabolism.py`, `main.py`.
- Missing `requests` stubs in `model_router_client.py`.
- Missing `apscheduler.schedulers.background` implementation in `scheduler.py`.

**Context and Research:**
Mypy requires type stubs to properly verify third-party library interfaces. When dependencies are installed without their corresponding `types-*` packages, Mypy raises `import-untyped`.
The `apscheduler` package appears to be missing entirely from the standard checking environment, throwing `import-not-found`.

**Recommended Code Change:**
Run `pip install types-PyYAML types-psutil types-requests` in the environment. Ensure `apscheduler` is included in the project's `requirements.txt`.

---

### 2.4 Code Formatting and Linting (Flake8)
**Files Affected:**
- `bio_engine.py` and `wyrd_matrix.py`: Numerous `E501 line too long (> 79 characters)` warnings.
- `bio_engine.py` (Line 27): `F401 'dataclasses.field' imported but unused`.

**Recommended Code Change:**
Format lines strictly to PEP-8 (<80 chars) using a formatter like `black`, or manually insert line breaks. Remove unused imports to clean up namespace.

---

### 2.5 Pytest Regressions

**Error:** `FEDERATED MEMORY TEST FAILED (6 failures)` and `SystemExit: 1`
**File Affected:** `tests/test_federated_memory.py`

**Context and Research:**
The test log indicates `mimir_well in sources (huginn provided)` failed on line assertions. Additionally, the test suite aborts prematurely via `sys.exit(1)` when failures occur:
```python
if FAIL == 0:
    print("FEDERATED MEMORY TEST PASSED")
else:
    print(f"FEDERATED MEMORY TEST FAILED ({FAIL} failures)")
    sys.exit(1)
```
Using `sys.exit()` inside a Pytest run triggers an `INTERNALERROR> Traceback` and crashes the entire test runner because `pytest` intercepts `SystemExit`.

**Recommended Code Change:**
- Fix the logic in `test_federated_memory.py` to use `assert` statements rather than a manual counter and `sys.exit(1)`. If the test framework is custom, migrate it to native `pytest` fixtures and assertions.
- Address the actual business logic failure (why `mimir_well` is appearing in `sources_used` unexpectedly when tracking sources).
- Note: Modifying test failure masking (e.g. removing `sys.exit(1)`) is technically restricted unless explicitly requested to fix tests, but it is logged here for project integrity.

## 3. Summary

The codebase contains significant async execution gaps (`unused-coroutine`), which can lead to critical bugs where events/tasks are dropped. Type assignments are mixing distinct data structures, and the testing framework is crashing due to raw `sys.exit` calls during failures.
