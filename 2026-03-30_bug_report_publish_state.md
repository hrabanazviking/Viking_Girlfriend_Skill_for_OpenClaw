# Bug Report: `RuntimeWarning: coroutine 'StateBus.publish_state' was never awaited`

**Date:** 2026-03-30

## Issue Description
During a codebase scan for potential bugs, it was discovered that numerous modules throughout the project are calling `bus.publish_state(event, nowait=True)` (or `self._bus.publish_state(event, nowait=True)`) synchronously within their `publish()` or utility methods.

Because `publish_state` is a coroutine, calling it as a standard synchronous function without `await` or without scheduling it on the `asyncio` event loop results in a `RuntimeWarning: coroutine was never awaited`. As a result, these critical state events are never actually executed or published to the `StateBus`.

This violates the core architecture principle stated in the system memory:
> "The project's internal state events are published via an asynchronous state bus. Methods like `bus.publish_state` are coroutines and must be explicitly `await`ed to prevent 'unused-coroutine' runtime bugs and ensure state updates process correctly."

## Impact
State updates from key systems such as `dream_engine`, `environment_mapper`, `ethics`, `memory_store`, `model_router_client`, `project_generator`, `prompt_synthesizer`, `scheduler`, `security`, and `trust_engine` are silently failing to propagate across the system, potentially causing logic failures or stale data within the OpenClaw companion framework.

## Affected Files
1. `viking_girlfriend_skill/scripts/dream_engine.py` (line 387)
2. `viking_girlfriend_skill/scripts/environment_mapper.py` (line 267)
3. `viking_girlfriend_skill/scripts/ethics.py` (line 490)
4. `viking_girlfriend_skill/scripts/memory_store.py` (lines 1006, 1216)
5. `viking_girlfriend_skill/scripts/model_router_client.py` (line 1267)
6. `viking_girlfriend_skill/scripts/project_generator.py` (line 231)
7. `viking_girlfriend_skill/scripts/prompt_synthesizer.py` (lines 430, 740, 907)
8. `viking_girlfriend_skill/scripts/scheduler.py` (line 436)
9. `viking_girlfriend_skill/scripts/security.py` (line 508)
10. `viking_girlfriend_skill/scripts/trust_engine.py` (lines 588, 764)

## Research and Technical Insights
Based on online research from sources like [Rotational Labs](https://rotational.io/blog/spooky-asyncio-errors-and-how-to-fix-them/):
* **Why it happens:** In Python's `asyncio`, an `async def` function returns a coroutine object when called. It does not execute the code inside the function until it is explicitly awaited or scheduled.
* **The Warning:** When the coroutine object is created but never used, the Python garbage collector eventually cleans it up and emits the `RuntimeWarning`.
* **The Fix:** Coroutines must be executed either via the `await` keyword (if inside another `async` function) or scheduled via the event loop (e.g., using `asyncio.run()`, `loop.create_task()`, or `loop.run_until_complete()`).

## Recommended Code Changes
To fix these instances where an asynchronous method (`publish_state`) is called from within a synchronous context (e.g., a standard `def publish(self, bus) -> None:` method), the call must be wrapped in a robust event loop handling block. This pattern is already successfully utilized elsewhere in the project (e.g., `cove_pipeline.py`):

```python
import asyncio
try:
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(bus.publish_state(event, nowait=True))
    else:
        loop.run_until_complete(bus.publish_state(event, nowait=True))
except RuntimeError:
    asyncio.run(bus.publish_state(event, nowait=True))
```

This ensures the coroutine is always properly scheduled regardless of the current event loop state.
