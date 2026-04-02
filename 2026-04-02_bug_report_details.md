# Bug Report Details: 2026-04-02

## Overview
A comprehensive pylint scan of the `viking_girlfriend_skill/scripts/` directory revealed several code quality issues, anti-patterns, and potential bugs. While the specific bugs mentioned in a previous report (`2026-03-22_bug_report.md` regarding E1124, E1120, and E0602) appear to have been resolved, numerous structural and linting issues remain. This report details the most severe or recurring issues and provides recommended code changes based on best practices.

## Major Pylint Issues and Recommendations

### 1. W0718: Catching too general exception `Exception` (broad-exception-caught)
**Description:** This warning occurs when a try-except block uses a naked `except Exception:` clause.
**Frequency:** This is the most frequently occurring warning across the entire codebase, heavily present in almost every module (e.g., `main.py`, `mimir_well.py`, `scheduler.py`, `cove_pipeline.py`).
**Impact:** Catching *all* exceptions can inadvertently mask critical bugs (like `NameError`, `TypeError`, or `ValueError`) and make debugging significantly harder. It also catches system-exiting exceptions unless carefully written (though `Exception` is safer than a bare `except:`, it is still an anti-pattern when overused).
**Recommendation:**
- Refactor `except Exception as exc:` blocks to catch specific exceptions anticipated from the enclosed code (e.g., `requests.exceptions.RequestException` for network calls, `json.JSONDecodeError` for parsing, `KeyError` for dictionary lookups).
- Where a broad exception is genuinely necessary as a last-resort fallback to prevent the system from crashing (e.g., in the main event loop or top-level scheduler tasks), consider logging the full traceback (`logger.exception("...")`) and re-raising if the state becomes irrecoverable.

### 2. R0401: Cyclic import (cyclic-import)
**Description:** Detected when two or more modules attempt to import each other, creating a circular dependency.
**Location:** Detected between `scripts.model_router_client` and `scripts.vordur`.
**Impact:** Cyclic imports can lead to `ImportError` or `AttributeError` at runtime, as Python may attempt to access attributes of a module that hasn't finished initializing. The current codebase mitigates this using many in-function (`import outside toplevel`) statements (C0415), which is a symptom of architectural entanglement.
**Recommendation:**
- **Refactoring:** Untangle the dependency graph. Identify the shared dependencies that cause `model_router_client` and `vordur` to rely on each other. Move these shared constants, interfaces, or helper functions into a third, independent module (e.g., `scripts.common` or `scripts.interfaces`) that both can import safely.
- Continue using local (inside-function) imports as a temporary band-aid only if refactoring the architecture is immediately infeasible, but aim to resolve the root cause.

### 3. R0902: Too many instance attributes (too-many-instance-attributes)
**Description:** Emitted when a class has more instance attributes than the pylint default (usually 7).
**Locations:** Found heavily in core data structures and managers, such as `mimir_well.MimirWell` (26/7), `oracle` (27/7), and `cove_pipeline` classes.
**Impact:** Classes with too many attributes often violate the Single Responsibility Principle (SRP) and can become difficult to maintain, test, and understand.
**Recommendation:**
- Review classes triggering this warning. If the attributes naturally group together into logical sub-components, extract them into separate data classes or smaller helper classes. For example, in `MimirWell`, attributes related purely to ChromaDB connection state could be grouped into a `ChromaDBConnection` object, while circuit breaker tracking could be delegated entirely to the circuit breaker objects.
- If the attributes are genuinely necessary and cohesive for a specific "God class" by design, the warning can be locally suppressed using `# pylint: disable=too-many-instance-attributes`, but refactoring should be the first choice.

### 4. C0302: Too many lines in module (too-many-lines)
**Description:** Modules exceeding the default line limit (1000 lines).
**Locations:** `scripts.mimir_well` (2322 lines), `scripts.vordur` (2099 lines), `scripts.model_router_client` (1353 lines), `scripts.memory_store` (1273 lines), `scripts.wyrd_matrix` (1325 lines).
**Impact:** Giant files are hard to navigate and often indicate that a module is taking on too many responsibilities.
**Recommendation:** Break these monolithic files into smaller, focused modules within sub-packages (e.g., refactor `mimir_well.py` into a `mimir_well/` directory containing `store.py`, `retrieval.py`, `health.py`, etc.).

### 5. C0415: Import outside toplevel
**Description:** Imports placed inside functions rather than at the top of the file.
**Frequency:** Hundreds of instances, particularly in `main.py`'s initialization routines and `model_router_client.py`.
**Impact:** While useful for breaking circular imports or deferring slow imports, pervasive use makes dependencies hard to track and can slightly impact performance if placed in hot loops (though Python caches modules).
**Recommendation:** Fix the architectural issues causing circular dependencies (see R0401) to allow modules to be imported cleanly at the top of the file.

### 6. Duplicate Code (R0801: Similar lines in 2 files)
**Description:** Pylint detected identical blocks of code copied across multiple files.
**Locations:** The async state publishing logic (involving `asyncio.get_event_loop()`, `loop.is_running()`, `loop.create_task()`, etc.) is duplicated across `metabolism.py`, `huginn.py`, `vordur.py`, `cove_pipeline.py`, `mimir_well.py`, `ethics.py`, `scheduler.py`, `dream_engine.py`, `memory_store.py`, `environment_mapper.py`, and `project_generator.py`.
**Recommendation:** Extract this identical async publishing boilerplate into a single utility function (perhaps in `state_bus.py` or a new `utils.py`) and import/call it from all these modules. This will centralize error handling and reduce code bloat.

## Conclusion
The Ørlög Architecture's implementation is highly complex, leading to massive files, circular dependencies, and a heavy reliance on broad exception catching for stability. To improve long-term maintainability, the project should focus on decoupling these systems (resolving cyclic imports), breaking down the largest files into sub-packages, and implementing more precise exception handling.