# Codebase Bug Report (2026-04-20)

## Overview
This document contains a summary of issues found in the codebase using static analysis tools (`pylint`, `flake8`, `mypy`, and `bandit`). It also includes recommended code changes for each significant issue.

## 1. Type Checking Issues (Mypy)
Mypy discovered several critical type errors and logical bugs.

### Unused Coroutines
Several coroutines are being called without an `await` statement, which means they are not actually executed.
**Files affected:**
- `trust_engine.py` (lines 588, 764)
- `security.py` (line 508)
- `scheduler.py` (line 436)
- `project_generator.py` (line 231)
- `ethics.py` (line 490)
- `dream_engine.py` (line 387)
- `environment_mapper.py` (line 267)
- `model_router_client.py` (line 1267)
- `prompt_synthesizer.py` (lines 430, 740, 907)
- `memory_store.py` (line 1006)

**Recommendation:**
Review these method calls in the async functions and prefix them with `await` (e.g., `await self.bus.publish_state(...)`). If called from synchronous code, wrap them appropriately using `asyncio.run()`, `loop.create_task()`, or `loop.run_until_complete()`.

### Attribute and Type Errors
- **`security.py:612`**: Incompatible types in assignment (expression has type "frozenset[str]", variable has type "set[str]").
  **Recommendation:** Update the variable type annotation or convert the `frozenset` to a `set` during assignment.
- **`vordur.py`**: Errors on lines 687, 1298, and 1881 indicate accessing `.complete` on a variable that might be `None`. Error on line 774 indicates `scripts.mimir_well` has no attribute `VerdictLabel`.
  **Recommendation:** Add proper null-checks (e.g., `if var is not None:`) before accessing `.complete`. Ensure `VerdictLabel` is imported or defined correctly in `mimir_well.py`.
- **`cove_pipeline.py:364`**: Name `draft` already defined on line 318.
  **Recommendation:** Rename one of the variables to avoid shadowing/re-definition bugs.
- **`main.py:511-530`**: Incompatible types in assignment for `WyrdState` updates. Various attributes (`phase_name`, `energy_modifier`, `narrative_hint`, `prompt_fragment`, `prompt_summary`) are missing from the `WyrdState` class definition, but the code attempts to assign/read them via instances of `BioState`, `DreamState`, and `OracleState`.
  **Recommendation:** Ensure `BioState`, `DreamState`, and `OracleState` either subclass `WyrdState` or ensure the target variable expects a Union type. Make sure the WyrdState (or subclasses) explicitly declare the missing attributes.
- **`main.py:635`**: Need type annotation for "messages" (`messages: list[dict] = ...`).
  **Recommendation:** Add the proper type hint `messages: list[dict[str, str]] = []`.

## 2. Security Vulnerabilities (Bandit)
Bandit reported SSRF/Path Traversal vulnerabilities related to `urllib.request.urlopen`.

**Files affected:**
- `viking_girlfriend_skill/data/knowledge_reference/populate.py` (lines 27, 62)

**Vulnerability:**
B310: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is unexpected and can lead to Local File Inclusion (LFI) or Server-Side Request Forgery (SSRF).

**Recommendation:**
Add explicit validation for the URL scheme to ensure it starts with `http://` or `https://` before calling `urlopen`. Once validated, append `# nosec B310` to the line to silence the Bandit warning.
```python
if not url.startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response: # nosec B310
    data = json.loads(response.read().decode())
```

## 3. Linting and Code Quality Issues (Pylint / Flake8)

- **Line Length:** Extensive line length violations (E501) mostly in `vordur.py` and `wyrd_matrix.py`. Many lines exceed 100 characters.
  **Recommendation:** Break down long statements, use implicit string concatenation, or format lists/dicts across multiple lines to adhere to PEP-8.
- **Too Many Instance Attributes / Too Many Locals:** Classes in `wyrd_matrix.py` and functions in `main.py` (e.g., `_process_loop` having 34 locals) exceed standard complexity metrics.
  **Recommendation:** Refactor complex functions into smaller helper functions. Group related instance attributes into data classes.
- **Broad Exception Catching:** Extensive use of `except Exception:` (W0718) in `wyrd_matrix.py` and `main.py`.
  **Recommendation:** Catch specific exceptions instead of the base `Exception` to avoid hiding unrelated bugs (like `KeyboardInterrupt` or `SystemExit` if using `BaseException`, though `Exception` is slightly better).
- **Global Statement:** `W0603` global statement usage in `wyrd_matrix.py`.
  **Recommendation:** Avoid global mutable state. Use class attributes, pass variables as arguments, or use a dependency injection pattern.
- **Naming Conventions:** Variables like `_turn_count` in `main.py` should be UPPER_CASE if they are module-level constants. `_BEHAVIOR_MAP` in `wyrd_matrix.py` should be snake_case if it's a local variable.
  **Recommendation:** Rename variables to follow PEP-8 conventions.

## Conclusion and Next Steps
1. Immediate priority should be fixing the **Unused Coroutines** to ensure the asynchronous state bus publishes events correctly. This is likely causing silent failures in the application logic.
2. Address the **Type and Attribute Errors** reported by mypy to prevent runtime crashes (especially `AttributeError` from missing fields or `NoneType` issues).
3. Apply the **Security Fix** for the `urllib.request.urlopen` calls in `populate.py`.
4. Run tests (`PYTHONPATH=./viking_girlfriend_skill pytest tests/`) to ensure the fixes don't cause regressions.
