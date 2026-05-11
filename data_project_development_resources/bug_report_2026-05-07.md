# Bug and Issue Report - 2026-05-07

## Security Vulnerabilities (Bandit)

### B310 in `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line 27)
**Issue:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
**Research:** B310 checks for urllib.urlopen usage without restricting the URL scheme. Allowing file:// or custom schemes can lead to Server-Side Request Forgery (SSRF) or local file inclusion. From Bandit documentation: 'Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.'
**Recommended Change:** Explicitly validate the URL scheme (e.g., ensuring it starts with `http://` or `https://`) to prevent B310 SSRF/Path Traversal vulnerabilities before appending `# nosec B310` to suppress Bandit warnings.

### B310 in `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line 62)
**Issue:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
**Research:** B310 checks for urllib.urlopen usage without restricting the URL scheme. Allowing file:// or custom schemes can lead to Server-Side Request Forgery (SSRF) or local file inclusion. From Bandit documentation: 'Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.'
**Recommended Change:** Explicitly validate the URL scheme (e.g., ensuring it starts with `http://` or `https://`) to prevent B310 SSRF/Path Traversal vulnerabilities before appending `# nosec B310` to suppress Bandit warnings.

## Type Checking Errors (Mypy)

### Unused Coroutine in `viking_girlfriend_skill/scripts/trust_engine.py` (Line 588)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/trust_engine.py` (Line 764)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/security.py` (Line 508)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/scheduler.py` (Line 436)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/project_generator.py` (Line 231)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/ethics.py` (Line 490)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/dream_engine.py` (Line 387)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/environment_mapper.py` (Line 267)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/model_router_client.py` (Line 1267)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/prompt_synthesizer.py` (Line 430)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/prompt_synthesizer.py` (Line 740)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/prompt_synthesizer.py` (Line 907)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.

### Unused Coroutine in `viking_girlfriend_skill/scripts/memory_store.py` (Line 1006)
**Issue:** Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
**Research:** Coroutines in Python (async/await) must be awaited or scheduled to run using an event loop (e.g., `asyncio.create_task` or `loop.create_task`). Failing to do so results in the coroutine never executing.
**Recommended Change:** Explicitly `await` the coroutine if inside an async context, or schedule it correctly using `loop.create_task` or `loop.run_until_complete` if running synchronously, to prevent 'unused-coroutine' runtime bugs.
