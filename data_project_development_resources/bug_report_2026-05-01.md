# Viking Girlfriend Skill Code Audit and Bug Report

**Date:** 2026-05-01

This report outlines issues discovered during a comprehensive codebase scan, including static security testing, type checking, and test execution validation.

## 1. Security Vulnerabilities: Bandit B310 (Insecure URL Open)
### Description
Bandit identified potential Server Side Request Forgery (SSRF) vulnerabilities related to the use of `urllib.request.urlopen` in `viking_girlfriend_skill/data/knowledge_reference/populate.py`.

### Research Findings
`urllib.request.urlopen` supports opening not just `http://` and `https://` URLs, but also `ftp://` and `file://`. If user input or external data is passed without validation, an attacker might manipulate the URL to read local files on the host machine or access internal network resources. As referenced in CWE-918 (Server-Side Request Forgery) and the Python DeepSource B310 documentation, URLs should be validated to ensure they use an expected scheme (e.g., `http` or `https`) prior to opening.

### Recommended Code Changes
Validate the URL scheme before calling `urlopen`. Once validated, add a `# nosec B310` comment to suppress the Bandit warning.

```python
if not url.lower().startswith("http"):
    raise ValueError("Invalid URL scheme. Only HTTP/HTTPS are permitted.")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    data = json.loads(response.read().decode())
```

## 2. Type Checking Errors: Mypy Unused Coroutines
### Description
The `mypy` scan reported multiple `[unused-coroutine]` errors across several files, including `trust_engine.py`, `security.py`, `scheduler.py`, `ethics.py`, `dream_engine.py`, `environment_mapper.py`, `prompt_synthesizer.py`, and `memory_store.py`.

### Research Findings
Mypy generates an `unused-coroutine` error when a function defined with `async def` is called but the resulting coroutine object is not awaited or scheduled. As noted in the mypy documentation and various Python troubleshooting resources (like GeeksforGeeks on RuntimeWarning: Coroutine Was Never Awaited), failing to `await` a coroutine means the code within it will not execute. This is a critical logical bug, especially in state management or side-effect producing functions.

### Recommended Code Changes
Ensure that all asynchronous method calls are properly `await`ed in async contexts, or properly scheduled in an event loop using `asyncio.create_task()` or `loop.run_until_complete()` if called from synchronous code.

Example from `trust_engine.py`:
```python
# Before
self.save_trust_state()

# After
await self.save_trust_state()
```

## 3. Type Checking Errors: Mypy Attribute Access and Typing
### Description
`mypy` found multiple attribute access errors in `viking_girlfriend_skill/scripts/main.py` related to `WyrdState` assignment. Waiters for variables initially typed as `BioState`, `DreamState`, or `OracleState` were reassigned to a `WyrdState` typed variable, which lacks attributes like `phase_name`, `energy_modifier`, `prompt_fragment`, and `prompt_summary`. Additional issues included missing type annotations for lists and union-attribute errors in `vordur.py`. Furthermore, `prompt_synthesizer.py` returned a flat list instead of the expected `Tuple[List[Dict[str, str]], VerificationMode]`, causing unpacking errors.

### Recommended Code Changes
1. Refactor assignments in `main.py` to use dynamically typed or locally scoped variables, or ensure a unified `WyrdState` base type correctly encompasses needed properties.
2. Fix `build_messages` call unpacking in `main.py` to expect `messages, mode = synth.build_messages(...)`.
3. Fix the `vordur.py` union-attribute errors by using `if item is not None:` checks before accessing the `.complete` attribute.

## 4. Test Framework Issues: Pytest SystemExit Abortions
### Description
During the `pytest` run, the test session unexpectedly aborted with a `SystemExit: 1` exception originating from `tests/test_huginn.py` and other test files.

### Research Findings
Using `sys.exit()` in Python code terminates the interpreter. When `sys.exit()` is used within a Pytest test case (often as an assertion failure alternative), it raises a `SystemExit` exception. Pytest catches this as an internal error, which disrupts the entire test collection and execution session, preventing subsequent tests from running.

### Recommended Code Changes
Replace `sys.exit(1)` calls inside test files with standard exception raising (e.g., `raise AssertionError("Test failed")`) or `pytest.fail("Test failed")`. This allows Pytest to register the specific test as a failure and safely continue running the remaining test suite.

```python
# Before
if FAIL != 0:
    print(f"HUGINN TEST FAILED ({FAIL} failures)")
    sys.exit(1)

# After
if FAIL != 0:
    raise AssertionError(f"HUGINN TEST FAILED ({FAIL} failures)")
```
