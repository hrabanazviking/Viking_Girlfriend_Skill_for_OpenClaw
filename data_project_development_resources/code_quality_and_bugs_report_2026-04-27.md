# Code Quality and Bug Report (2026-04-27)

## 1. Security Issues (Bandit)

- **MEDIUM** in `viking_girlfriend_skill/data/knowledge_reference/populate.py:27`: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
  - **Recommendation**: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen
- **MEDIUM** in `viking_girlfriend_skill/data/knowledge_reference/populate.py:62`: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
  - **Recommendation**: https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

## 2. Type Checking Issues (Mypy)

- viking_girlfriend_skill/scripts/config_loader.py:24: error: Library stubs not installed for "yaml"  [import-untyped]
- viking_girlfriend_skill/scripts/trust_engine.py:588: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/trust_engine.py:588: note: Are you missing an await?
- viking_girlfriend_skill/scripts/trust_engine.py:764: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/trust_engine.py:764: note: Are you missing an await?
- viking_girlfriend_skill/scripts/security.py:508: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/security.py:508: note: Are you missing an await?
- viking_girlfriend_skill/scripts/security.py:612: error: Incompatible types in assignment (expression has type "frozenset[str]", variable has type "set[str]")  [assignment]
- viking_girlfriend_skill/scripts/scheduler.py:436: error: Value of type "Coroutine[Any, Any, None]" must be used  [unused-coroutine]
- viking_girlfriend_skill/scripts/scheduler.py:436: note: Are you missing an await?
- ... and 47 more issues.

## 3. Style and Linting Issues (Flake8 & Pylint)

Found 1905 Flake8 issues and 1128 Pylint issues.
Common themes include:
- Unused imports
- Line length violations
- Missing docstrings
- Too many nested blocks or instance attributes

## 4. Research on Identified Bugs

### Bandit B310 (urllib urlopen)
The `urllib.request.urlopen` function can open `file://` or `ftp://` URLs as well as standard HTTP/HTTPS URLs. This presents a Server-Side Request Forgery (SSRF) risk or allows attackers to read local files if the URL parameter can be manipulated. **Recommendation**: Validate that the URL starts with `http://` or `https://` before opening it. If it is statically hardcoded and safe, a `# nosec B310` comment can be added.

### Mypy `[unused-coroutine]`
Mypy is reporting that an async function is being called but its result (the coroutine) is not being `await`ed or scheduled. This is a common bug where a developer forgets the `await` keyword, causing the asynchronous task to never actually execute. **Recommendation**: Add the `await` keyword before the coroutine call, or schedule it appropriately using `asyncio.create_task()` or similar if it's meant to run in the background.
