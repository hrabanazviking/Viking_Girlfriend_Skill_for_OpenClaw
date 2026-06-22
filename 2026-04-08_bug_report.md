# Bug Report for Viking Girlfriend Skill

## Overview
This document contains potential bugs, code quality issues, and recommended changes found through static analysis (Flake8, Pylint, Bandit, and Mypy).

## Mypy Errors (Type Checking)

- trust_engine.py:588: error: Value of type 'Coroutine[Any, Any, None]' must be used [unused-coroutine]
- security.py:508: error: Value of type 'Coroutine[Any, Any, None]' must be used [unused-coroutine]
- scheduler.py:436: error: Value of type 'Coroutine[Any, Any, None]' must be used [unused-coroutine]
- main.py:511: error: Incompatible types in assignment (expression has type 'BioState', variable has type 'WyrdState')
- vordur.py:774: error: Module 'scripts.mimir_well' has no attribute 'VerdictLabel'

## Pylint Warnings (Code Quality)

- environment_mapper.py:441:4: W0603: Using the global statement (global-statement)
- metabolism.py:657:4: W0603: Using the global statement (global-statement)
- metabolism.py:1:0: R0801: Similar lines in 2 files (duplicate-code)
- scheduler.py:536:15: W0718: Catching too general exception Exception (broad-exception-caught)

## Flake8 Issues (Style)

- vordur.py:1703:80: E501 line too long (88 > 79 characters)
- wyrd_matrix.py:16:80: E501 line too long (84 > 79 characters)

## Recommended Changes

- **Missing awaits**: In `trust_engine.py`, `security.py`, `scheduler.py`, `project_generator.py`, `ethics.py`, `dream_engine.py`, `environment_mapper.py`, `model_router_client.py`, `prompt_synthesizer.py`, and `memory_store.py`, ensure methods like `bus.publish_state()` are properly awaited when called within an async context, or wrapped in task creation.
- **Attribute Errors**: Fix `main.py` where variables are incorrectly assigned to `WyrdState` but typed as `BioState`, `DreamState`, or `OracleState`, resulting in missing attributes.
- **Global variables**: Avoid global statement warnings in `scheduler.py`, `environment_mapper.py`, and `metabolism.py`.
- **Duplicate code**: Refactor the state publication logic (e.g. `try ... loop.create_task ...`) that is duplicated across 11 files into a central utility method, perhaps in `state_bus.py`.
- **Typing issues**: Fix type annotations and imports (e.g., missing stub packages for yaml, psutil).

## Research Findings

### Mypy "unused-coroutine" Error
According to Python's official `asyncio` documentation, when a coroutine function is called but not awaited (e.g. `coro()` instead of `await coro()`) or not scheduled using `asyncio.create_task()`, the coroutine will not execute. This leads to `RuntimeWarning: coroutine was never awaited` and Mypy's `unused-coroutine` error.

**Best Practice:** The usual fix is to either `await` the coroutine directly if in an async context:
```python
async def main():
    await test()
```
Or use `asyncio.create_task(coro())` to schedule it concurrently. For our case where `bus.publish_state()` is sometimes called from synchronous or potentially overlapping event loops, the existing `try... loop.create_task... except...` logic is partially correct but duplicated. Ensuring we correctly `await` it inside async methods and consistently use a utility wrapper for synchronous methods will resolve both the code duplication and the Mypy errors.

### Pylint "global-statement" Warning
The `W0603` warning occurs when using the `global` keyword. In the context of `environment_mapper.py` and `metabolism.py`, it often points to poorly encapsulated state that could lead to unintended side effects, particularly in concurrent/async applications.

**Best Practice:** State should generally be encapsulated within classes or explicitly passed as arguments instead of relying on global module-level variables. This improves code testability and reliability in multithreaded/async environments.

## Additional Finding: E2E Pipeline and Prompt Synthesizer Issue
The E2E tests and prompt synthesizer tests fail due to a `TypeError` in `PromptSynthesizer.build_messages`.
According to system memory and the traceback (`messages = [self.Message(m["role"], m["content"]) for m in messages_raw]`), `PromptSynthesizer.build_messages()` returns a tuple `(messages_raw, verification_mode)`, not just a list of messages. The tests (and potentially the `main.py` pipeline) incorrectly assume it returns a list directly, leading to `TypeError: list indices must be integers or slices, not str` when trying to parse what is actually the `verification_mode` tuple element or when iterating over the tuple incorrectly.

**Recommended Fix:** Ensure all callers of `build_messages()` properly unpack the tuple, e.g., `messages_raw, mode = synth.build_messages(...)`.
