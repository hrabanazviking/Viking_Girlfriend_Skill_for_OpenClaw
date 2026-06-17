# Code Scan Report 2026-05-03

## Potential Bugs Found

- viking_girlfriend_skill/scripts/trust_engine.py:588: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/trust_engine.py:764: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/security.py:508: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/security.py:612: error: Incompatible types in assignment (expression has type "frozenset[str]", variable has type "set[str]")  [assignment]
- viking_girlfriend_skill/scripts/scheduler.py:436: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/project_generator.py:231: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/ethics.py:490: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/dream_engine.py:387: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/runtime_kernel.py:291: error: Cannot infer type of lambda  [misc]
- viking_girlfriend_skill/scripts/environment_mapper.py:267: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/vordur.py:687: error: Item "None" of "Any | None" has no attribute "complete"  [union-attr]
- viking_girlfriend_skill/scripts/vordur.py:774: error: Module "scripts.mimir_well" has no attribute "VerdictLabel"  [attr-defined]
- viking_girlfriend_skill/scripts/vordur.py:1298: error: Item "None" of "Any | None" has no attribute "complete"  [union-attr]
- viking_girlfriend_skill/scripts/vordur.py:1881: error: Item "None" of "Any | None" has no attribute "complete"  [union-attr]
- viking_girlfriend_skill/scripts/model_router_client.py:1267: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/prompt_synthesizer.py:430: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/prompt_synthesizer.py:740: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/prompt_synthesizer.py:907: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/memory_store.py:1006: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/cove_pipeline.py:364: error: Name "draft" already defined on line 318  [no-redef]
- viking_girlfriend_skill/scripts/main.py:511: error: Incompatible types in assignment (expression has type "BioState", variable has type "WyrdState")  [assignment]
- viking_girlfriend_skill/scripts/main.py:512: error: "WyrdState" has no attribute "phase_name"  [attr-defined]
- viking_girlfriend_skill/scripts/main.py:512: error: "WyrdState" has no attribute "energy_modifier"  [attr-defined]
- viking_girlfriend_skill/scripts/main.py:512: error: "WyrdState" has no attribute "narrative_hint"  [attr-defined]
- viking_girlfriend_skill/scripts/main.py:520: error: Incompatible types in assignment (expression has type "DreamState", variable has type "WyrdState")  [assignment]
- viking_girlfriend_skill/scripts/main.py:521: error: "WyrdState" has no attribute "prompt_fragment"  [attr-defined]
- viking_girlfriend_skill/scripts/main.py:522: error: "WyrdState" has no attribute "prompt_fragment"  [attr-defined]
- viking_girlfriend_skill/scripts/main.py:529: error: Incompatible types in assignment (expression has type "OracleState", variable has type "WyrdState")  [assignment]
- viking_girlfriend_skill/scripts/main.py:530: error: "WyrdState" has no attribute "prompt_summary"  [attr-defined]
- viking_girlfriend_skill/scripts/main.py:635: error: Need type annotation for "messages" (hint: "messages: list[<type>] = ...")  [var-annotated]

## Analysis and Recommended Code Changes

### Unused Coroutines
Several scripts trigger a mypy `[unused-coroutine]` error:
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

**Cause**: An `async def` function is being called without an `await`, returning a coroutine object instead of the awaited result. The coroutine is never executed. This often happens with internal event bus methods like `bus.publish_state`.
**Recommendation**: Make sure to explicitly `await` these calls if the surrounding function is `async`. If the surrounding function is synchronous, you must correctly schedule the execution (e.g. `asyncio.create_task` or `asyncio.run()`).

### `vordur.py` union-attr issues
- lines 687, 1298, 1881: `Item "None" of "Any | None" has no attribute "complete"`
**Cause**: Mypy warns that a variable might be `None` when its `.complete` method/property is accessed.
**Recommendation**: Add a check `if variable is not None:` before accessing its attributes, or verify the prior logic guarantees it isn't `None` and use `assert variable is not None`.

### `vordur.py` attr-defined issue
- line 774: `Module "scripts.mimir_well" has no attribute "VerdictLabel"`
**Cause**: Trying to access `VerdictLabel` from `scripts.mimir_well` when it isn't defined there or exported.
**Recommendation**: Ensure `VerdictLabel` is defined in `mimir_well.py` and properly exported, or update the import to point to the correct module where `VerdictLabel` is actually defined.

### `cove_pipeline.py` no-redef issue
- line 364: `Name "draft" already defined on line 318`
**Cause**: The variable `draft` is being redeclared/reassigned in a way that violates scoping rules or shadows another important definition, or is redefined with a different type.
**Recommendation**: Use a different variable name (e.g., `updated_draft` or `draft_v2`) to avoid confusing mypy and ensure clarity in the code.

### `main.py` state assignment issues
- lines 511-530: Incompatible types in assignment for `WyrdState`, `BioState`, `DreamState`, `OracleState`. "WyrdState has no attribute..."
**Cause**: A variable declared as or inferred as `WyrdState` is being assigned a subclass/different state type (`BioState`, `DreamState`, `OracleState`), and then attributes specific to those subclasses are being accessed. Mypy expects the variable to strictly conform to `WyrdState` unless explicitly typed as a Union or if type narrowing isn't happening properly.
**Recommendation**: Ensure the variable is typed to allow for these specific states (e.g., `Union[BioState, DreamState, OracleState]`), or use explicit type casting if necessary.

### `security.py` assignment issue
- line 612: `Incompatible types in assignment (expression has type "frozenset[str]", variable has type "set[str]")`
**Cause**: Trying to assign an immutable `frozenset` to a variable expected to be a mutable `set`.
**Recommendation**: Either change the variable type hint to accept `frozenset[str]`, or explicitly cast the `frozenset` back to a `set` (e.g., `variable = set(the_frozenset)`).

### `main.py` missing type annotation
- line 635: `Need type annotation for "messages"`
**Cause**: Mypy cannot infer the type of an empty list or dictionary (`messages = []`).
**Recommendation**: Add a type hint: `messages: list[dict[str, str]] = []` (or whatever the actual type is).

### `runtime_kernel.py` lambda inference
- line 291: `Cannot infer type of lambda`
**Cause**: A lambda function lacks explicit type definitions, and Mypy can't figure it out from context.
**Recommendation**: Provide an explicit type hint for the variable holding the lambda, or replace the lambda with a standard `def` function with proper type hints.

## Research on Mypy `[unused-coroutine]`
The `[unused-coroutine]` error in mypy occurs when an asynchronous function (returning a `Coroutine`) is called, but its return value is neither awaited nor assigned to a variable, nor scheduled for execution. In Python, calling an `async def` function does not execute it; it merely returns a coroutine object. If this object is ignored, the asynchronous code is never run, leading to a silent bug where state updates, API calls, or other asynchronous operations simply do not occur.

This often happens with event publishing methods like `publish_state`, where developers used to synchronous code might just call `bus.publish_state("some_state")` and forget to `await` it.
