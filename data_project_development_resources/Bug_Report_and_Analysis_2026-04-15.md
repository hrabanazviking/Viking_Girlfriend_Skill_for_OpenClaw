# Bug Report & Analysis - 2026-04-15

## 1. Unawaited Coroutines (`[unused-coroutine]`)
**Issue:** Several modules call async functions without awaiting them. This leads to the function returning a coroutine object instead of executing, causing silent failures.
**Locations:**
- `viking_girlfriend_skill/scripts/trust_engine.py`: lines 588, 764
- `viking_girlfriend_skill/scripts/security.py`: line 508
- `viking_girlfriend_skill/scripts/scheduler.py`: line 436
- `viking_girlfriend_skill/scripts/project_generator.py`: line 231
- `viking_girlfriend_skill/scripts/ethics.py`: line 490
- `viking_girlfriend_skill/scripts/dream_engine.py`: line 387
- `viking_girlfriend_skill/scripts/environment_mapper.py`: line 267
- `viking_girlfriend_skill/scripts/model_router_client.py`: line 1267
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py`: lines 430, 740, 907
- `viking_girlfriend_skill/scripts/memory_store.py`: line 1006

**Recommended Fix:**
Add the `await` keyword before these async function calls, or use `asyncio.create_task` if they are meant to run concurrently in the background.

## 2. Incompatible Type Assignments (`main.py`)
**Issue:** Mypy reports type assignment errors because state variables (`BioState`, `DreamState`, `OracleState`) are being assigned to a variable expected to be `WyrdState`.
**Locations:**
- `viking_girlfriend_skill/scripts/main.py`: lines 511, 512, 520, 521, 522, 529, 530

**Recommended Fix:**
Use distinct variables for different state types, or use a common base class/union type like `Union[WyrdState, BioState, DreamState, OracleState]`.

## 3. Name Redefinition (`cove_pipeline.py`)
**Issue:** A variable `draft` is redefined on line 364, shadowing a previous definition on line 318.
**Location:**
- `viking_girlfriend_skill/scripts/cove_pipeline.py`: line 364

**Recommended Fix:**
Rename the inner variable to avoid shadowing, e.g., `current_draft`.

## 4. Unused Local Variables
**Issue:** Several variables are assigned but never used, cluttering the code and potentially indicating logical errors where a variable should have been used.
**Locations:**
- `prompt_synthesizer.py:688`: `target_chars`
- `trust_engine.py:682`: `key`
- `vordur.py:776`: `VL`
- `vordur.py:1694`: `contradiction_records`

**Recommended Fix:**
Remove the unused variables if they are not needed, or verify if they were meant to be used in subsequent logic.

## 5. Potential Security Vulnerability (B310)
**Issue:** Bandit detected a potential security issue related to `urllib.request.urlopen` in `populate.py`. Without URL scheme validation, this can lead to SSRF or local file inclusion via `file://` schemas.
**Location:**
- `viking_girlfriend_skill/data/knowledge_reference/populate.py`

**Resolution:**
Already fixed during the investigation by adding scheme validation and a `# nosec B310` comment.

## 6. Pytest Assertions (Test Failures)
**Issue:** The test framework had tests explicitly calling `sys.exit(1)`, which causes the test runner to abort entirely.
**Locations:**
- `tests/test_federated_memory.py`
- `tests/test_huginn.py`

**Resolution:**
Already fixed during the investigation by replacing `sys.exit(1)` with `pytest.fail("Test failed")` and ensuring `import pytest` is present.
