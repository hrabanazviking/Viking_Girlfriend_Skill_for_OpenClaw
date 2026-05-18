# Security Scan and Bug Report (2026-05-18)

## 1. Bandit Vulnerability: B310 in `populate.py`

### Description
In `viking_girlfriend_skill/data/knowledge_reference/populate.py`, there are two instances of a high-confidence, medium-severity vulnerability (`B310`). The `urllib.request.urlopen` function is called directly on `req` where `url` might not be restricted.
- Line 27: `with urllib.request.urlopen(req) as response:`
- Line 62: `with urllib.request.urlopen(req) as response:`

### Security Research
Using `urllib.request.urlopen` without explicitly validating the URL scheme can expose the application to Server Side Request Forgery (SSRF) and Path Traversal. By default, `urlopen` supports handlers for `http://`, `https://`, `ftp://`, and `file://`. If an attacker can manipulate the URL, they could use `file://` to read local files on the system. This corresponds to CWE-22 (Improper Limitation of a Pathname to a Restricted Directory) and CWE-918 (Server-Side Request Forgery).

### Recommended Fix
Validate that the URL explicitly starts with `http://` or `https://` before attempting to open it. Once validated, add a Bandit suppression comment `# nosec B310` to indicate the issue has been resolved safely.

```python
if not url.lower().startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme provided: {url}")
# ...
with urllib.request.urlopen(req) as response:  # nosec B310
    data = json.loads(response.read().decode())
```

---

## 2. Mypy Type Error: Unused Coroutine `bus.publish_state`

### Description
A static type check with Mypy flagged several instances of the `[unused-coroutine]` error:
`Value of type "Coroutine[Any, Any, None]" must be used`
`note: Are you missing an await?`

This occurs because `bus.publish_state(...)` is an asynchronous coroutine method, but it is being called synchronously without awaiting or properly scheduling it in several modules. This will lead to the coroutine never executing, meaning state events won't be published.

Affected files based on scan:
- `viking_girlfriend_skill/scripts/trust_engine.py` (lines 588, 764)
- `viking_girlfriend_skill/scripts/security.py` (line 508)
- `viking_girlfriend_skill/scripts/scheduler.py` (line 436)
- `viking_girlfriend_skill/scripts/project_generator.py` (line 231)
- `viking_girlfriend_skill/scripts/ethics.py` (line 490)
- `viking_girlfriend_skill/scripts/dream_engine.py` (line 387)

### Recommended Fix
Modify the lines invoking `bus.publish_state(event, nowait=True)`.
If the enclosing function is defined as `async def`, simply prefix the call with `await`:
```python
await bus.publish_state(event, nowait=True)
```
If the enclosing function is synchronous, you must correctly schedule the coroutine onto the running event loop:
```python
loop = asyncio.get_event_loop()
if loop.is_running():
    loop.create_task(bus.publish_state(event, nowait=True))
else:
    asyncio.run(bus.publish_state(event, nowait=True))
```

---

## 3. Mypy Type Error: Incompatible Types in Assignment in `security.py`

### Description
In `viking_girlfriend_skill/scripts/security.py` at line 612, the type hint for `_TEXT_INJECTABLE_FILES` is `Set[str]`, but the actual assigned value is a `frozenset`.
```python
_TEXT_INJECTABLE_FILES: Set[str] = frozenset({
    "last_dream.json",
    "association_cache.json",
    "object_states.json",
})
```

Mypy flags this as an incompatible assignment error since `frozenset` is immutable and does not satisfy the mutable `Set` interface constraint (which in Python typing corresponds to `set`).

### Recommended Fix
Update the type annotation to match the assigned type by importing `frozenset` type hinting correctly if on older python, or simply change `Set[str]` to `frozenset[str]` for modern typing.

```python
_TEXT_INJECTABLE_FILES: frozenset[str] = frozenset({
    "last_dream.json",
    "association_cache.json",
    "object_states.json",
})
```
