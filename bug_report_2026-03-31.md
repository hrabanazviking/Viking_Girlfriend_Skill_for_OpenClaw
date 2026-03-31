# Bug Report & Analysis (2026-03-31)

## Summary
A comprehensive security and quality scan of the codebase has been performed. This document details the discovered issues, context from documentation, and recommended code changes.

## 1. Security Vulnerabilities (Bandit Scan)
**Files Affected:**
- `viking_girlfriend_skill/data/knowledge_reference/populate.py`

**Issue:**
Using `urllib.request.urlopen(url)` without proper scheme sanitization.

**Description:**
Bandit identified an issue with `B310` concerning standard `urllib` opening of URLs. The `urlopen` call might execute an unintended scheme like `file://` if the provided URL is malformed or maliciously modified.

**Recommended Change:**
While the script hardcodes `https://en.wikipedia.org`, it's best practice to explicitly validate the URL scheme before calling `urlopen`.
```python
if not url.startswith("https://"):
    raise ValueError("Only HTTPS URLs are allowed")
```
Given this script is mostly an offline build tool (knowledge reference generator) and the URLs are constructed with a hardcoded `https://` prefix, the severity is relatively low in practice, but still needs addressing to maintain security best practices and keep Bandit happy.

## 2. Unawaited Coroutines (`publish_state` bug)
**Files Affected:**
- `viking_girlfriend_skill/scripts/ethics.py`
- `viking_girlfriend_skill/scripts/trust_engine.py`
- `viking_girlfriend_skill/scripts/dream_engine.py`
- `viking_girlfriend_skill/scripts/prompt_synthesizer.py`
- `viking_girlfriend_skill/scripts/memory_store.py`
- `viking_girlfriend_skill/scripts/project_generator.py`
- `viking_girlfriend_skill/scripts/security.py`
- `viking_girlfriend_skill/scripts/model_router_client.py`
- `viking_girlfriend_skill/scripts/scheduler.py`
- `viking_girlfriend_skill/scripts/environment_mapper.py`

**Issue:**
Multiple occurrences of `self.bus.publish_state(event)` without an `await`.

**Description:**
In Python `asyncio`, calling an `async def` function creates a coroutine object but does not schedule or execute it until it's `await`ed. By omitting `await`, the `publish_state` function is never run. This directly correlates to the internal system memory: "Methods like `bus.publish_state` are coroutines and must be explicitly `await`ed to prevent 'unused-coroutine' runtime bugs and ensure state updates process correctly."

**Recommended Change:**
Search for instances of `.publish_state(` in the AST where the expression is not part of an `await` node and modify them to `await self.bus.publish_state(...)`.

## 3. General Code Quality (Pylint & Flake8)
**Issue:**
Numerous "line too long" violations (E501/C0301) and "Catching too general exception Exception" (W0718). There are also missing dependencies causing Pylint to fail (E0401) for `psutil`, `litellm`, `chromadb`, `requests`, and `ollama`.

**Description:**
The project relies on external libraries that were not installed in the standard environment. The code structure and length violate PEP-8 standard conventions, notably line length.

**Recommended Change:**
- Fix `requirements.txt` to include `psutil`, `litellm`, `chromadb`, `requests`, `ollama`. (If these are already in `viking_girlfriend_skill/requirements.txt`, install them using `pip install -r viking_girlfriend_skill/requirements.txt` to get cleaner Pylint results).
- Perform a reformatting using tools like `black` or `autopep8` to fix line length issues without manually rewriting hundreds of lines.
- Review broad exception catching where specifically scoped exceptions could prevent hard-to-debug logic errors.

## Recommended Action Plan
1. Fix the Bandit warnings in `populate.py` by adding URL schema validation.
2. Resolve all unawaited `publish_state` coroutines across all script files.
3. Update `requirements.txt` if any of the flagged modules (`psutil`, `litellm`, `requests`, etc.) are legitimately missing.
