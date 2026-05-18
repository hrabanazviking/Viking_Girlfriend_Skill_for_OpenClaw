# Viking Girlfriend Skill - Security and Code Quality Report (2026-05-02)

## 1. Security Vulnerabilities (Bandit SAST)

### B310 - Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **Severity:** MEDIUM
- **Confidence:** HIGH
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line 27)
- **Code Snippet:**
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```
- **Recommendation:** Ensure URL scheme validation (e.g., `startswith('http://')` or `startswith('https://')`) before using `urllib.request.urlopen`. Append `# nosec B310` to the specific line if false positive.

### B310 - Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **Severity:** MEDIUM
- **Confidence:** HIGH
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line 62)
- **Code Snippet:**
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```
- **Recommendation:** Ensure URL scheme validation (e.g., `startswith('http://')` or `startswith('https://')`) before using `urllib.request.urlopen`. Append `# nosec B310` to the specific line if false positive.

## 2. Type Errors and Concurrency Bugs (Mypy)

Mypy identified several critical `unused-coroutine` errors. These indicate that asynchronous functions are being called without an `await`, leading to them never being executed. This can cause significant runtime failures in state propagation.

- `viking_girlfriend_skill/scripts/trust_engine.py:588: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/trust_engine.py:764: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/security.py:508: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/scheduler.py:436: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/project_generator.py:231: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/ethics.py:490: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/dream_engine.py:387: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/environment_mapper.py:267: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/model_router_client.py:1267: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py:430: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py:740: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py:907: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`
- `viking_girlfriend_skill/scripts/memory_store.py:1006: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]`

**Recommendation:** Use `await` when calling these coroutines within an `async` function. If called from a synchronous function, use `asyncio.create_task()` or schedule it on the running event loop.

## 3. Style and Import Errors (Flake8 & Pylint)

Several files contain unused imports and structural issues. Notably:
- `viking_girlfriend_skill/data/knowledge_reference/populate.py:5:1: F401 'sys' imported but unused`
- `viking_girlfriend_skill/scripts/bio_engine.py:27:1: F401 'dataclasses.field' imported but unused`
- `viking_girlfriend_skill/scripts/config_loader.py:20:1: F401 'dataclasses.field' imported but unused`
- `viking_girlfriend_skill/scripts/cove_pipeline.py:37:1: F401 'os' imported but unused`
- `viking_girlfriend_skill/scripts/cove_pipeline.py:39:1: F401 'time' imported but unused`
- `viking_girlfriend_skill/scripts/cove_pipeline.py:44:1: F401 'typing.Union' imported but unused`
- `viking_girlfriend_skill/scripts/dream_engine.py:31:1: F401 'dataclasses.field' imported but unused`
- `viking_girlfriend_skill/scripts/ethics.py:24:1: F401 're' imported but unused`
- `viking_girlfriend_skill/scripts/huginn.py:47:1: F401 'dataclasses.field' imported but unused`
- `viking_girlfriend_skill/scripts/huginn.py:49:1: F401 'typing.Union' imported but unused`
- `viking_girlfriend_skill/scripts/metabolism.py:31:1: F401 'dataclasses.field' imported but unused`
- `viking_girlfriend_skill/scripts/mimir_well.py:1288:17: F401 'chromadb' imported but unused`
- `viking_girlfriend_skill/scripts/model_router_client.py:60:1: F401 'json' imported but unused`
- `viking_girlfriend_skill/scripts/model_router_client.py:65:1: F401 'traceback' imported but unused`
- `viking_girlfriend_skill/scripts/oracle.py:31:1: F401 'dataclasses.field' imported but unused`
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py:46:1: F401 'time' imported but unused`
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py:47:1: F401 'dataclasses.field' imported but unused`
- `viking_girlfriend_skill/scripts/runtime_kernel.py:24:1: F401 'scripts.comprehensive_logging.get_comprehensive_logger' imported but unused`
- `viking_girlfriend_skill/scripts/runtime_kernel.py:26:1: F401 'scripts.state_bus.get_bus' imported but unused`
- `viking_girlfriend_skill/scripts/scheduler.py:31:1: F401 'dataclasses.field' imported but unused`
- `viking_girlfriend_skill/scripts/state_bus.py:20:1: F401 'hashlib' imported but unused`
- `viking_girlfriend_skill/scripts/state_bus.py:26:1: F401 'typing.Dict' imported but unused`
- `viking_girlfriend_skill/scripts/state_bus.py:26:1: F401 'typing.List' imported but unused`
- `viking_girlfriend_skill/scripts/vordur.py:53:1: F401 'typing.Union' imported but unused`

**Recommendation:** Remove unused imports to clean up the codebase. Address missing dependencies (e.g., `psutil`, `litellm`, `chromadb`, `requests`, `ollama`) to ensure correct functionality and type checking.


## 4. Web Research on Identified Bugs

### Bandit B310: Audit url open for permitted schemes
- **Source:** OpenStack Bandit documentation and community discussions (e.g., Stack Overflow).
- **Details:** The `urllib.request.urlopen` function in Python can open local files using the `file://` scheme. If a URL is user-controlled, this can lead to a path traversal or Server-Side Request Forgery (SSRF) vulnerability.
- **Resolution Strategy:** Explicitly validate that the URL scheme begins with `http://` or `https://` before opening. Since Bandit uses a simple blacklist for the function call itself, appending `# nosec B310` is necessary after performing the validation to silence the warning.

### Mypy unused-coroutine error
- **Source:** Mypy official documentation.
- **Details:** Mypy ensures that return values of `async def` functions are not ignored. Failing to use or `await` the return value of a coroutine is usually a programming error because the coroutine will not actually execute unless it is awaited or scheduled on an event loop.
- **Resolution Strategy:** Use `await` when calling the function from another `async` function. If called from synchronous code, it should be wrapped in `asyncio.run()`, `asyncio.create_task()`, or scheduled on a running event loop to ensure it is properly executed.
