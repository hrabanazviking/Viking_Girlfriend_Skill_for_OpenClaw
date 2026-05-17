# Code Quality and Security Audit Report - 2026-05-04

## Overview
This report summarizes the findings from a comprehensive scan of the codebase, which included static security analysis (Bandit) and type checking (mypy).

## Findings

### 1. Missing Async Awaits (Unused Coroutines)
**Tool**: mypy (`unused-coroutine`)
**Severity**: High (Runtime Bugs)
**Description**: Several internal state event publishers (`bus.publish_state()`) are not awaited or scheduled properly. According to project memory, since these methods are coroutines (or can be async contexts), failing to schedule them correctly can lead to dropped events and "unused-coroutine" warnings, severely affecting the OpenClaw framework integration.
**Affected Files**:
- `viking_girlfriend_skill/scripts/trust_engine.py`
- `viking_girlfriend_skill/scripts/security.py`
- `viking_girlfriend_skill/scripts/scheduler.py`
- `viking_girlfriend_skill/scripts/project_generator.py`
- `viking_girlfriend_skill/scripts/ethics.py`
- `viking_girlfriend_skill/scripts/dream_engine.py`
- `viking_girlfriend_skill/scripts/environment_mapper.py`
- `viking_girlfriend_skill/scripts/model_router_client.py`
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py`
- `viking_girlfriend_skill/scripts/memory_store.py`

**Recommended Code Change**: Wrap the synchronous `publish_state` calls in an `asyncio` task creation block:
```python
try:
    _loop = asyncio.get_running_loop()
    _loop.create_task(self._bus.publish_state(event, nowait=True))
except RuntimeError:
    asyncio.run(self._bus.publish_state(event, nowait=True))
```

### 2. URL Open Vulnerability (Bandit B310)
**Tool**: Bandit (`B310`)
**Severity**: Medium (SSRF / Path Traversal)
**Description**: Using `urllib.request.urlopen` without validating the URL scheme can allow local file access (`file://` or custom schemes) leading to Server-Side Request Forgery or path traversal if user input is manipulated.
**Affected File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py` (lines 27, 62)

**Recommended Code Change**: Add an explicit URL scheme validation check prior to opening the request, and suppress the warning via `# nosec B310`.
```python
if not url.lower().startswith('http'):
    raise ValueError('URL must be HTTP or HTTPS')
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    ...
```
