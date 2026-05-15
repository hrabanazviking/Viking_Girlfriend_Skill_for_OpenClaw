# Viking Girlfriend Skill - Security and Bug Analysis Report
**Date:** 2026-03-25

## Executive Summary
This report summarizes the static analysis (SAST), linting, and type-checking issues found in the `viking_girlfriend_skill/scripts/` codebase. Tools utilized for this assessment included `mypy`, `flake8`, and `bandit`.

Overall, the codebase exhibited minimal severe security vulnerabilities, but several programmatic bugs and type-checking issues were identified that pose a risk to system stability, particularly around async coroutine handling and internal state updates.

## Identified Issues & Recommended Code Changes

### 1. Unused Coroutines (`unused-coroutine`)
**Description:** Across multiple files (`trust_engine.py`, `security.py`, `scheduler.py`, `project_generator.py`, `ethics.py`, `dream_engine.py`, `environment_mapper.py`, `model_router_client.py`, `prompt_synthesizer.py`, `memory_store.py`), mypy flagged that the coroutine returned by `bus.publish_state(event, nowait=True)` was not awaited or assigned.

**Context/Research:** According to mypy documentation, this is a programmatic error where an asynchronous function is called without an `await`, meaning the function's execution is not actually scheduled or awaited at runtime. This will lead to state updates silently failing to propagate on the state bus.
**Recommended Change:** Since these are generally called from synchronous contexts (like `def publish(self):`), and the `bus` expects async, we should use `asyncio.create_task` or a similar background task executor to run the coroutine without blocking, or refactor the caller to be asynchronous. Given the codebase has loops, `asyncio.create_task(bus.publish_state(event, nowait=True))` or `asyncio.ensure_future(...)` is the typical fix for fire-and-forget inside async loops, or using the `loop.create_task` if a loop exists. A more systemic fix in the `publish` wrapper methods is needed. However, since the code specifically says `nowait=True`, it seems intended to be fire-and-forget. The codebase usually handles this by:
```python
try:
    loop = asyncio.get_running_loop()
    loop.create_task(self._bus.publish_state(event, nowait=True))
except RuntimeError:
    asyncio.run(self._bus.publish_state(event, nowait=True))
```

### 2. Type Inference on Lambdas (`runtime_kernel.py:291`)
**Description:** `mypy` cannot infer the type of the `lambda` function used for signal handling: `lambda s=sig: asyncio.create_task(self.shutdown(reason=f"signal:{s.name}"))`
**Context/Research:** Mypy requires explicit type annotations for lambda parameters when it cannot infer them from context.
**Recommended Change:** Annotate the `s` parameter in the lambda. `lambda s=sig: ...` -> `lambda s=sig: ...` but lambda type annotations in python can be tricky. Alternatively, replace the lambda with a proper nested `def` or use `functools.partial`.
```python
def handle_sig(s: signal.Signals = sig) -> None:
    asyncio.create_task(self.shutdown(reason=f"signal:{s.name}"))
loop.add_signal_handler(sig, handle_sig)
```

### 3. Incompatible Types in Assignment (`security.py:612`)
**Description:** `_TEXT_INJECTABLE_FILES: Set[str] = frozenset({...})` causes a type conflict because `frozenset` is incompatible with `set` (which implies mutability).
**Recommended Change:** Update the type hint to `frozenset[str]`.
```python
_TEXT_INJECTABLE_FILES: frozenset[str] = frozenset({
    "last_dream.json",
    "association_cache.json",
    "object_states.json",
})
```

### 4. Shadowing / Type Overwriting (`main.py:511-530`)
**Description:** The variable `s` is repeatedly reassigned to hold different state objects (`BioState`, `DreamState`, `OracleState`), but mypy infers it initially as `WyrdState`.
**Recommended Change:** Use uniquely named variables for each state extraction to avoid type pollution.
```python
s_bio = get_bio_engine().get_state()
...
s_dream = get_dream_engine().get_state()
...
s_oracle = get_oracle().get_daily_oracle()
```

### 5. Missing Type Annotations (`main.py:635`)
**Description:** `messages = []` lacks a type hint, causing `Need type annotation for "messages"` error.
**Recommended Change:** Annotate the variable.
```python
messages: List[Message] = []
```

### 6. Missing Imports and Redefinitions
- `vordur.py:774`: `Module "scripts.mimir_well" has no attribute "VerdictLabel"`. `VerdictLabel` was moved or belongs to `vordur.py` natively.
  **Recommended Change:** Fix the import path or remove the import if it's locally available in `vordur.py`.
- `cove_pipeline.py:364`: `draft` variable is redefined.
  **Recommended Change:** Rename the second `draft` or just assign to it without type-hinting if already declared.
- `vordur.py:687, 1298, 1881`: `self._router` might be `None` when `complete` is called.
  **Recommended Change:** Guard `self._router.complete` calls with `if self._router is not None:` or assert it.

## Conclusion
The bugs listed above represent the most critical programmatic errors that interrupt static type checking and potentially runtime execution (such as the unawaited bus publishing coroutines). Addressing these will bring the codebase up to full `mypy` compliance and ensure robust background state tracking.
