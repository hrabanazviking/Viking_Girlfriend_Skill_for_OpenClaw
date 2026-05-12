# Bug and Security Scan Report
Date: 2026-05-08

## Summary
A comprehensive security and bug scan was performed on the codebase.

## Findings

### 1. Bandit Security Issue: B310 (urllib.request.urlopen)
**Location:**
- `viking_girlfriend_skill/data/knowledge_reference/populate.py:27`
- `viking_girlfriend_skill/data/knowledge_reference/populate.py:62`

**Description:**
Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. The `urllib.request.urlopen` function is vulnerable to Server Side Request Forgery (SSRF) and local file inclusion if the URL isn't properly validated to ensure it uses the `http://` or `https://` schemes.

**Research Insights:**
The `urllib.request` module's `urlopen` function can open various protocols, not just `http://` or `https://`. It also supports `ftp://` and importantly `file://`. If user input or external, unverified data controls the URL passed to `urlopen`, an attacker could potentially force the application to read arbitrary local files on the server (e.g., `file:///etc/passwd`) or make requests to internal services that should not be exposed externally (SSRF).
* See: [CVE-2019-9740](https://nvd.nist.gov/vuln/detail/cve-2019-9740)
* See: [DeepSource BAN-B310](https://deepsource.com/directory/python/issues/BAN-B310)

**Recommended Code Change:**
Before opening a URL with `urllib.request.urlopen`, the URL scheme must be explicitly validated to ensure it starts with `http://` or `https://`. If it is valid, the operation can proceed, and we can append `# nosec B310` to suppress the Bandit warning.

Example fix:
```python
if not url.lower().startswith(('http://', 'https://')):
    raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are allowed.")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    data = json.loads(response.read().decode())
```

### 2. MyPy Unused Coroutine Errors
**Locations:**
- `viking_girlfriend_skill/scripts/trust_engine.py:588`, `764`
- `viking_girlfriend_skill/scripts/security.py:508`
- `viking_girlfriend_skill/scripts/scheduler.py:436`
- `viking_girlfriend_skill/scripts/project_generator.py:231`
- `viking_girlfriend_skill/scripts/ethics.py:490`
- `viking_girlfriend_skill/scripts/dream_engine.py:387`
- `viking_girlfriend_skill/scripts/environment_mapper.py:267`

**Description:**
"Value of type 'Coroutine[Any, Any, None]' must be used" error. This means an async function (a coroutine) was called without being `await`ed.

**Research Insights:**
In Python's `asyncio`, calling an `async def` function does not immediately execute it; instead, it returns a coroutine object. To actually run the function and get its result, it must be `await`ed or scheduled on the event loop (e.g., using `asyncio.create_task`). Failing to do so means the function's logic is never executed, which can lead to silent failures, missing state updates, or resource leaks.
In this project, methods like `bus.publish_state` are coroutines and must be explicitly `await`ed or properly scheduled.

**Recommended Code Change:**
Review each location where the coroutine is called and either prepend `await` (if in an async context) or correctly schedule it (e.g., `asyncio.create_task(...)` or `loop.run_until_complete(...)`) if running synchronously.

### 3. Pylint Line Length and Docstring Issues
**Location:** Multiple files (e.g., `viking_girlfriend_skill/scripts/wyrd_matrix.py`)

**Description:**
Various Pylint warnings including `Line too long` (C0301) and `Missing function or method docstring` (C0116).

**Research Insights:**
Adhering to PEP 8 standards (e.g., line lengths of 79 or 100 characters) and providing descriptive docstrings improves code readability, maintainability, and consistency.

**Recommended Code Change:**
Refactor long lines by breaking them into multiple lines or using appropriate continuation characters. Add meaningful docstrings to all functions and methods to explain their purpose, arguments, and return values.
