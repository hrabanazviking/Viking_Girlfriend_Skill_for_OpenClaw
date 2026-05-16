# Codebase Scan Report (2026-05-16)

## Overview
A comprehensive scan of the codebase was performed using static analysis tools (Bandit, Flake8, Pylint, Mypy) to identify potential bugs, vulnerabilities, style issues, and type errors.

## Identified Issues

### 1. Bandit Vulnerabilities: B310 (Audit url open for permitted schemes)
- **Files Affected:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Lines 27, 62)
- **Description:** The `urllib.request.urlopen` function is used to open URLs directly from user or external sources without validating the scheme. This allows for potential Server-Side Request Forgery (SSRF) or local file read via `file://` or custom schemes.
- **Recommendation:** Implement scheme validation before calling `urlopen`. Ensure the URL starts with `http://` or `https://`. Also append `# nosec B310` to suppress Bandit warnings after validation is added.
- **Proposed Code Change:**
  ```python
  if not url.startswith(('http://', 'https://')):
      raise ValueError("Invalid URL scheme")
  with urllib.request.urlopen(req) as response:  # nosec B310
  ```

### 2. Mypy Type Checking Errors: unused-coroutine
- **Files Affected:**
  - `viking_girlfriend_skill/scripts/trust_engine.py` (Lines 588, 764)
  - `viking_girlfriend_skill/scripts/security.py` (Line 508)
  - `viking_girlfriend_skill/scripts/scheduler.py` (Line 436)
  - `viking_girlfriend_skill/scripts/project_generator.py` (Line 231)
  - `viking_girlfriend_skill/scripts/ethics.py` (Line 490)
  - `viking_girlfriend_skill/scripts/dream_engine.py` (Line 387)
- **Description:** Mypy reported multiple instances of `Value of type "Coroutine[Any, Any, None]" must be used`. This typically occurs when an asynchronous function (coroutine) is called but the resulting coroutine object is not `await`ed or scheduled to run. This results in a `RuntimeWarning: coroutine was never awaited` at runtime, and the underlying operation is never actually executed.
- **Recommendation:** If inside an `async` function, use `await` when calling the coroutine. If calling from synchronous code or scheduling a fire-and-forget task, use appropriate event loop methods like `asyncio.create_task()`, `asyncio.run()`, or the framework's equivalent execution mechanism.
- **Proposed Code Change:**
  Ensure functions like `bus.publish_state()` or other async operations are awaited:
  ```python
  await bus.publish_state(...)
  # OR if fire-and-forget inside synchronous code
  loop = asyncio.get_event_loop()
  loop.create_task(bus.publish_state(...))
  ```

### 3. Missing Type Stubs (Mypy)
- **Files Affected:** `config_loader.py` (yaml), `oracle.py` (yaml), `metabolism.py` (psutil), `bio_engine.py` (yaml), `scheduler.py` (apscheduler.schedulers.background)
- **Description:** Mypy is unable to find type stubs for several third-party libraries (`yaml`, `psutil`, `apscheduler`).
- **Recommendation:** Install the respective types packages (e.g., `types-PyYAML`, `types-psutil`) or add `# type: ignore` comments if stubs are unavailable. Add them to `requirements.txt` if necessary.

### 4. Pylint and Flake8 Warnings
- **Description:** Multiple style and complexity warnings were identified.
  - `wyrd_matrix.py`: Too many lines (>1000), too many instance attributes, missing docstrings, and invalid naming conventions (`DECAY_PER_TURN`).
  - `generate_wave3_docs.py`: Numerous lines exceeding the 79 character limit.
- **Recommendation:** Refactor `wyrd_matrix.py` to extract classes into separate files, add comprehensive docstrings, and rename constants/attributes to adhere to PEP8 guidelines. Break long lines in `generate_wave3_docs.py`.

## Research Notes
- **Bandit B310:** According to DeepSource and Bandit documentation, `urlopen` can open `file://` schemes, making the application vulnerable to local file inclusion or Server-Side Request Forgery if the URL parameter is manipulated by an attacker. The standard mitigation is validating the URL scheme (e.g., checking for `http` or `https`) before attempting to open it.
- **Unused Coroutines:** GeeksForGeeks and SuperFastPython note that calling an `async def` function creates a coroutine object but does not execute it. Not awaiting it or wrapping it in a task causes the logic to be skipped and triggers a `RuntimeWarning: coroutine was never awaited`. Static checking tools like Mypy catch this early as `unused-coroutine`.
