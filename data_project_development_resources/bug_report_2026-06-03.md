# Codebase Bug and Vulnerability Report (2026-06-03)

This report documents identified bugs and vulnerabilities across the OpenClaw Viking Girlfriend Skill project, including security scanner (Bandit), static analyzer (mypy/pylint), and functional logic issues.

## Issue: viking_girlfriend_skill/data/knowledge_reference/populate.py
**CWE:** CWE-22 (Path Traversal) / CWE-73
**Description:** Bandit B310: Audit url open for permitted schemes. Use of `urllib.request.urlopen` without validating the URL scheme can lead to Path Traversal or SSRF vulnerabilities if the URL is dynamically generated or controlled by an attacker.
According to recent research (e.g., CVE-2026-45725 in Miggo Vulnerability Database), if `urllib.parse.urlparse` and path caching mechanisms are not properly sanitized, an attacker can supply 'file://' URLs or use `../` sequences to write to or read arbitrary local files, leading to arbitrary file write or Remote Code Execution.

**Recommendation:** Explicitly validate that the URL scheme starts with 'http://' or 'https://' before making the request. Additionally, ensure any path derived from the URL is sanitized (e.g. using `pathlib.PurePosixPath` and filtering out `..` sequences). Once validation is in place, append `# nosec B310` to suppress the Bandit warning.

---

## Issue: Multiple scripts across viking_girlfriend_skill/scripts/
**Description:** RuntimeWarning: coroutine was never awaited ('unused-coroutine' in mypy). The `publish_state` method on the state bus is asynchronous (`async def publish_state`), but it is being called synchronously in many scripts (e.g., `bus.publish_state(event, nowait=True)`). This means the coroutine is created but never executed, leading to events not being published and causing logic bugs.

**Recommendation:** To properly execute the coroutine in a synchronous context, you should use `asyncio.create_task` (if already in an event loop) or `asyncio.run` / `asyncio.get_event_loop().create_task()`, or use an explicit wrapper like `get_bus().publish_state_sync()` if the state bus provides one.

---

## Issue: infra/bootstrap_host.py
**CWE:** CWE-78
**Description:** Bandit B404, B603: Use of `subprocess.run`. The use of the subprocess module requires caution as it can lead to command injection if untrusted inputs are passed.

**Recommendation:** Since the commands here appear to be hardcoded or static (e.g., checking tool versions), add `# nosec B404` to the import statement and `# nosec B603` to the `subprocess.run` calls to suppress these warnings.

---

## Issue: viking_girlfriend_skill/scripts/cove_pipeline.py
**Description:** mypy error: Name 'draft' already defined on line 318. The variable `draft` is declared as type `str` later in the function (`draft: str = checkpoint.draft or ""`), but it was already used earlier in the same scope (`draft = self._direct_draft(query, context)`).

**Recommendation:** Remove the type hint on line 364 in `cove_pipeline.py` (i.e., change `draft: str = checkpoint.draft or ""` to `draft = checkpoint.draft or ""`).

---

## Issue: viking_girlfriend_skill/scripts/vordur.py
**Description:** mypy error: Module 'scripts.mimir_well' has no attribute 'VerdictLabel'. Vordur checker references `VerdictLabel` from `mimir_well`, but `VerdictLabel` is actually defined within `vordur.py`.

**Recommendation:** Remove the import `from scripts.mimir_well import VerdictLabel as VL` and use the local `VerdictLabel` class instead.

---

## Issue: viking_girlfriend_skill/scripts/main.py
**Description:** mypy error: Incompatible types in assignment. `main.py` tries to assign `BioState`, `DreamState`, and `OracleState` to a variable annotated as `WyrdState` (which is likely missing these specific attributes).

**Recommendation:** Update type definitions or use a common base class/union type for these states.

---
