# Security and Code Quality Bug Report
## B310 blacklist

**File**: viking_girlfriend_skill/data/knowledge_reference/populate.py
**Line**: 27
**Severity**: MEDIUM
**Confidence**: HIGH

**Description**: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

**Code Snippet**:
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```

## B310 blacklist

**File**: viking_girlfriend_skill/data/knowledge_reference/populate.py
**Line**: 62
**Severity**: MEDIUM
**Confidence**: HIGH

**Description**: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

**Code Snippet**:
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```

## Flake8 Issues
```
viking_girlfriend_skill/data/knowledge_reference/populate.py:5:1: F401 'sys' imported but unused
viking_girlfriend_skill/scripts/bio_engine.py:27:1: F401 'dataclasses.field' imported but unused
viking_girlfriend_skill/scripts/config_loader.py:20:1: F401 'dataclasses.field' imported but unused
viking_girlfriend_skill/scripts/cove_pipeline.py:37:1: F401 'os' imported but unused
viking_girlfriend_skill/scripts/cove_pipeline.py:39:1: F401 'time' imported but unused
viking_girlfriend_skill/scripts/cove_pipeline.py:44:1: F401 'typing.Union' imported but unused
viking_girlfriend_skill/scripts/dream_engine.py:31:1: F401 'dataclasses.field' imported but unused
viking_girlfriend_skill/scripts/ethics.py:24:1: F401 're' imported but unused
viking_girlfriend_skill/scripts/huginn.py:47:1: F401 'dataclasses.field' imported but unused
viking_girlfriend_skill/scripts/huginn.py:49:1: F401 'typing.Union' imported but unused
viking_girlfriend_skill/scripts/metabolism.py:31:1: F401 'dataclasses.field' imported but unused
viking_girlfriend_skill/scripts/mimir_well.py:1288:17: F401 'chromadb' imported but unused
viking_girlfriend_skill/scripts/model_router_client.py:60:1: F401 'json' imported but unused
viking_girlfriend_skill/scripts/model_router_client.py:65:1: F401 'traceback' imported but unused
viking_girlfriend_skill/scripts/oracle.py:31:1: F401 'dataclasses.field' imported but unused
viking_girlfriend_skill/scripts/prompt_synthesizer.py:46:1: F401 'time' imported but unused
viking_girlfriend_skill/scripts/prompt_synthesizer.py:47:1: F401 'dataclasses.field' imported but unused
viking_girlfriend_skill/scripts/prompt_synthesizer.py:688:9: F841 local variable 'target_chars' is assigned to but never used
viking_girlfriend_skill/scripts/runtime_kernel.py:24:1: F401 'scripts.comprehensive_logging.get_comprehensive_logger' imported but unused
viking_girlfriend_skill/scripts/runtime_kernel.py:26:1: F401 'scripts.state_bus.get_bus' imported but unused
viking_girlfriend_skill/scripts/scheduler.py:31:1: F401 'dataclasses.field' imported but unused
viking_girlfriend_skill/scripts/state_bus.py:20:1: F401 'hashlib' imported but unused
viking_girlfriend_skill/scripts/state_bus.py:26:1: F401 'typing.Dict' imported but unused
viking_girlfriend_skill/scripts/state_bus.py:26:1: F401 'typing.List' imported but unused
viking_girlfriend_skill/scripts/trust_engine.py:682:13: F841 local variable 'key' is assigned to but never used
viking_girlfriend_skill/scripts/vordur.py:53:1: F401 'typing.Union' imported but unused
viking_girlfriend_skill/scripts/vordur.py:776:13: F841 local variable 'VL' is assigned to but never used
viking_girlfriend_skill/scripts/vordur.py:1694:9: F841 local variable 'contradiction_records' is assigned to but never used
```
## Mypy Issues
```
viking_girlfriend_skill/scripts/config_loader.py:24: error: Library stubs not installed for "yaml"  [import-untyped]
viking_girlfriend_skill/scripts/trust_engine.py:588: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/trust_engine.py:764: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/security.py:508: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/security.py:612: error: Incompatible types in assignment (expression has type "frozenset[str]", variable has type "set[str]")  [assignment]
viking_girlfriend_skill/scripts/scheduler.py:436: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/scheduler.py:499: error: Cannot find implementation or library stub for module named "apscheduler.schedulers.background"  [import-not-found]
viking_girlfriend_skill/scripts/project_generator.py:231: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/oracle.py:36: error: Library stubs not installed for "yaml"  [import-untyped]
viking_girlfriend_skill/scripts/metabolism.py:35: error: Library stubs not installed for "psutil"  [import-untyped]
viking_girlfriend_skill/scripts/ethics.py:490: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/dream_engine.py:387: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/bio_engine.py:32: error: Library stubs not installed for "yaml"  [import-untyped]
viking_girlfriend_skill/scripts/runtime_kernel.py:291: error: Cannot infer type of lambda  [misc]
viking_girlfriend_skill/scripts/mimir_well.py:44: error: Library stubs not installed for "yaml"  [import-untyped]
viking_girlfriend_skill/scripts/environment_mapper.py:267: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/vordur.py:687: error: Item "None" of "Any | None" has no attribute "complete"  [union-attr]
viking_girlfriend_skill/scripts/vordur.py:774: error: Module "scripts.mimir_well" has no attribute "VerdictLabel"  [attr-defined]
viking_girlfriend_skill/scripts/vordur.py:1298: error: Item "None" of "Any | None" has no attribute "complete"  [union-attr]
viking_girlfriend_skill/scripts/vordur.py:1881: error: Item "None" of "Any | None" has no attribute "complete"  [union-attr]
viking_girlfriend_skill/scripts/model_router_client.py:518: error: Library stubs not installed for "requests"  [import-untyped]
viking_girlfriend_skill/scripts/model_router_client.py:1267: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/prompt_synthesizer.py:430: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/prompt_synthesizer.py:740: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/prompt_synthesizer.py:907: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/memory_store.py:1006: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
viking_girlfriend_skill/scripts/cove_pipeline.py:364: error: Name "draft" already defined on line 318  [no-redef]
viking_girlfriend_skill/scripts/main.py:68: error: Library stubs not installed for "psutil"  [import-untyped]
viking_girlfriend_skill/scripts/main.py:511: error: Incompatible types in assignment (expression has type "BioState", variable has type "WyrdState")  [assignment]
viking_girlfriend_skill/scripts/main.py:512: error: "WyrdState" has no attribute "phase_name"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:512: error: "WyrdState" has no attribute "energy_modifier"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:512: error: "WyrdState" has no attribute "narrative_hint"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:520: error: Incompatible types in assignment (expression has type "DreamState", variable has type "WyrdState")  [assignment]
viking_girlfriend_skill/scripts/main.py:521: error: "WyrdState" has no attribute "prompt_fragment"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:522: error: "WyrdState" has no attribute "prompt_fragment"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:529: error: Incompatible types in assignment (expression has type "OracleState", variable has type "WyrdState")  [assignment]
viking_girlfriend_skill/scripts/main.py:530: error: "WyrdState" has no attribute "prompt_summary"  [attr-defined]
viking_girlfriend_skill/scripts/main.py:635: error: Need type annotation for "messages" (hint: "messages: list[<type>] = ...")  [var-annotated]
Found 38 errors in 19 files (checked 26 source files)
```
## Recommendations & Research

### Bandit B310 (urllib urlopen)
- **Research**: Using `urllib.request.urlopen` with unvalidated user input or unchecked URLs can lead to Server-Side Request Forgery (SSRF) and Local File Inclusion (LFI) via the `file://` scheme. Attackers can use it to read local files (like `/etc/passwd`) or interact with internal network resources.
- **Recommendations**:
  - Explicitly validate that the URL starts with `http://` or `https://` before opening it.
  - If using a static/hardcoded internal URL, you can suppress the warning with `# nosec B310` after validating its safety.
  - Use modern, safer libraries like `requests` if feasible, configuring timeouts to prevent denial-of-service, though scheme validation is still required.

### Flake8 Unused Imports & Variables
- **Recommendations**:
  - Remove all unused imports reported as `F401` to clean up the namespace and slightly improve loading times.
  - Remove or appropriately utilize the unused variables reported as `F841` to avoid confusion and potential memory leaks in tight loops.

### Mypy Type Checking Errors
- **Research**: `[unused-coroutine]` errors occur when an asynchronous function or method (defined with `async def`) is called without being `await`ed. This means the coroutine object is created but never scheduled to run, leading to subtle bugs where the intended asynchronous action (like publishing state to a bus) simply does not execute.
- **Recommendations**:
  - `[unused-coroutine]`: Ensure that all asynchronous calls (like `state_bus.publish_state`) are either `await`ed inside an `async def` or correctly scheduled using `asyncio.create_task()` or `asyncio.run()` if called from synchronous code.
  - `[import-untyped]` and `[import-not-found]`: Install the corresponding type stubs (e.g., `types-PyYAML`, `types-psutil`, `types-requests`) and ensure packages like `apscheduler` are installed in the static analysis environment.
  - `[assignment]` errors (e.g., assigning `BioState` to a variable explicitly typed as `WyrdState`): If the variable is meant to hold multiple types of state objects, refactor the type annotation to use a Union (e.g., `WyrdState | BioState | DreamState | OracleState`) or generic base class, rather than forcing distinct dataclass types into a single restrictive variable type.

### External Research References
- Bandit B310: https://deepsource.com/directory/python/issues/BAN-B310 (Server Side Request Forgery)
