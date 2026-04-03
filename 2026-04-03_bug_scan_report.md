# Bug Scan Report (2026-04-03)

## 1. Pytest Test Session Abort `sys.exit(1)`
**Location:** `tests/test_federated_memory.py` line 366

**Description:**
The test file `tests/test_federated_memory.py` calls `sys.exit(1)` at the module level if there are test failures. In pytest, `sys.exit()` raises a `SystemExit` exception, which is caught by the test runner and abruptly ends the test session, causing an `INTERNALERROR> mainloop: caught unexpected SystemExit!`.

**Impact:**
When this test file fails, the rest of the test suite stops running. This masks other potential failures and breaks CI pipelines by not reporting standard test failure outputs.

**Recommended Code Change:**
Instead of calculating failures manually and calling `sys.exit(1)`, we should wrap the assertions in proper test functions (e.g., `def test_federated_memory_feature():`) and use standard `assert` statements or `pytest.fail()`. At the very least, remove the `sys.exit(1)` call and raise an `AssertionError` instead.

```python
<<<<<<< SEARCH
if FAIL == 0:
    print("FEDERATED MEMORY TEST PASSED")
else:
    print(f"FEDERATED MEMORY TEST FAILED ({FAIL} failures)")
    sys.exit(1)
=======
if FAIL == 0:
    print("FEDERATED MEMORY TEST PASSED")
else:
    print(f"FEDERATED MEMORY TEST FAILED ({FAIL} failures)")
    raise AssertionError(f"Federated Memory test failed with {FAIL} errors")
>>>>>>> REPLACE
```

## 2. Test Failure in Federated Memory (`mimir_well in sources`)
**Location:** `tests/test_federated_memory.py` line 355

**Description:**
The test `[15] sources_used tracking` is failing with the assertion error: `FAIL  mimir_well in sources (huginn provided)  [sources=['episodic_buffer', 'episodic_json']]`.

**Impact:**
The `mimir_well` is unexpectedly not present in `result.sources_used` when `huginn` is provided, which indicates a potential regression in the federated memory retrieval logic.

**Recommended Fix:**
Investigate `FederatedMemoryRequest` or `MemoryStore.retrieve_federated_memory()` logic in `viking_girlfriend_skill/scripts/memory_store.py` to see why `mimir_well` is not appending to `sources_used` when knowledge search is invoked.

## 3. Pylint Import Errors (Environment vs Code Bug)
**Description:**
Running `pylint` reveals several `E0401: Unable to import` errors.
- `psutil` in `main.py` and `metabolism.py`
- `litellm` in `prompt_synthesizer.py` and `memory_store.py`
- `chromadb` in `memory_store.py` and `mimir_well.py`
- `requests` in `model_router_client.py`
- `ollama` in `mimir_well.py`

**Analysis:**
These modules are correctly defined in `requirements.txt`. Some of these imports are correctly deferred (e.g., `import litellm` inside `_count_tokens()`) to allow parts of the system to load without heavy dependencies, which is a good design choice for optional capabilities.
No immediate action is needed, but the CI/CD pipeline should ensure all dependencies in `requirements.txt` are installed before linting to avoid false positives.

## 4. State Bus `nowait=True` Unhandled Dropped Events
**Location:** `viking_girlfriend_skill/scripts/state_bus.py` line 243

**Description:**
In `publish_state`, if the `_state` queue is full when `nowait=True` is passed, `asyncio.QueueFull` is caught and `self._state_dropped += 1` is incremented. However, there is no logging or alert that an event was silently dropped.

**Recommended Code Change:**
Add a logger warning so dropped events are visible for debugging.
```python
<<<<<<< SEARCH
            except asyncio.QueueFull:
                self._state_dropped += 1
                return
=======
            except asyncio.QueueFull:
                self._state_dropped += 1
                logger.warning(f"State queue full. Dropped event: {event.event_type}")
                return
>>>>>>> REPLACE
```
