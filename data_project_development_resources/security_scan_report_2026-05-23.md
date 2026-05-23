# Security and Bug Scan Report - 2026-05-23

## Overview
A comprehensive static analysis scan of the codebase was conducted using `bandit`, `mypy`, `pylint`, and `flake8`. Several bugs and security vulnerabilities were identified.

## 1. Security Vulnerabilities

### B310: Insecure URL Open (Server-Side Request Forgery - SSRF)
**File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Lines:** 27, 62
**Description:** The script uses `urllib.request.urlopen` with dynamically constructed URLs without first validating the URL scheme. This can allow an attacker to bypass intended protocols and access local files using `file://` or other custom schemes, leading to a Server-Side Request Forgery (SSRF) vulnerability.

**Recommended Code Change:**
Before opening the URL, explicitly validate that the URL scheme is `http` or `https`.
```python
import urllib.request
import urllib.parse
from urllib.parse import urlparse # Import urlparse

# ... inside fetch_category_members and fetch_extracts_in_batches ...

    parsed_url = urlparse(url)
    if parsed_url.scheme not in ['http', 'https']:
        raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}")

    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response: # nosec B310
# ...
```

## 2. Unused Coroutine Bugs
**Multiple Files:**
- `viking_girlfriend_skill/scripts/trust_engine.py` (lines 588, 764)
- `viking_girlfriend_skill/scripts/security.py` (line 508)
- `viking_girlfriend_skill/scripts/scheduler.py` (line 436)
- `viking_girlfriend_skill/scripts/project_generator.py` (line 231)
- `viking_girlfriend_skill/scripts/ethics.py` (line 490)
- `viking_girlfriend_skill/scripts/dream_engine.py` (line 387)
- `viking_girlfriend_skill/scripts/environment_mapper.py` (line 267)
- `viking_girlfriend_skill/scripts/model_router_client.py` (line 1267)
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py` (lines 430, 740, 907)
- `viking_girlfriend_skill/scripts/memory_store.py` (line 1006)

**Description:** MyPy analysis (`[unused-coroutine]`) reveals that `bus.publish_state(event, nowait=True)` is called synchronously without an `await` or without scheduling it on the event loop, despite it being a coroutine method in these instances. This results in the state events never actually being published to the bus.

**Recommended Code Change:**
Since these appear to be synchronous contexts or fire-and-forget, the coroutines should be scheduled using the event loop.
```python
import asyncio
# ...
    try:
        loop = asyncio.get_running_loop()
        loop.create_task(bus.publish_state(event, nowait=True))
    except RuntimeError:
        asyncio.run(bus.publish_state(event, nowait=True))
```

## 3. Mypy Typing & Missing Stub Errors
**Multiple Files:** Various missing library stubs (`yaml`, `psutil`, `requests`).
- `viking_girlfriend_skill/scripts/main.py`: `WyrdState` assignment errors where subclasses (e.g., `BioState`, `DreamState`, `OracleState`) are incorrectly typed or missing attributes.
- `viking_girlfriend_skill/scripts/vordur.py`: Missing `VerdictLabel` import from `mimir_well`.

**Recommended Code Change:**
Install missing stubs (`types-PyYAML`, `types-psutil`, `types-requests`) and fix type hinting.

## 4. Unused Variables (Flake8 F841)
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py:688`: `target_chars`
- `viking_girlfriend_skill/scripts/trust_engine.py:682`: `key`
- `viking_girlfriend_skill/scripts/vordur.py:776`: `VL`
- `viking_girlfriend_skill/scripts/vordur.py:1694`: `contradiction_records`

**Recommended Code Change:** Remove unused variables.
