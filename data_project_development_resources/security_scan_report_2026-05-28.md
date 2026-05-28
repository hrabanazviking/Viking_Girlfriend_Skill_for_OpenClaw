# Security Scan Report

**Date:** 2026-05-28

This report details the findings from a Bandit Static Application Security Testing (SAST) scan of the codebase, focusing on potential security vulnerabilities.

---

## 1. Subprocess Execution (B404, B603)
**Location:** `infra/bootstrap_host.py`
**Severity:** Low
**CWE:** CWE-78 (Improper Neutralization of Special Elements used in an OS Command)

**Details:**
- **B404**: `import subprocess` flags the use of the `subprocess` module, which can have security implications.
- **B603**: `subprocess.run([command, "--version"], capture_output=True, check=True)` calls a subprocess without `shell=True`. While safer than `shell=True`, it still requires that `command` is a trusted input.

**Research:**
According to Bandit documentation, B404 and B603 are low-severity warnings acting as reminders. `subprocess` can be safe if used without `shell=True` and if inputs are sanitized or hardcoded. If the input is untrusted, command injection could occur. If the inputs are static/trusted, this can be considered a false positive or acceptable risk.

**Recommended Code Changes:**
Ensure the `command` variable is explicitly validated or derived from a trusted source. If the usage is deemed safe, append `# nosec B404` to the import and `# nosec B603` to the `subprocess.run()` call to suppress the warnings.

```python
import subprocess  # nosec B404

# ...
subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
```

---

## 2. Unhandled Exceptions (B110: try_except_pass)
**Locations:**
- `tests/test_cove_pipeline.py`
- `tests/test_e2e_system.py`
**Severity:** Low
**CWE:** CWE-703 (Improper Check or Handling of Exceptional Conditions)

**Details:**
The codebase catches exceptions (`except Exception:`) and silences them with `pass`.
- In `tests/test_cove_pipeline.py`: `except Exception: pass`
- In `tests/test_e2e_system.py`: `except Exception: pass  # offline / loop not running — acceptable`

**Research:**
Bandit's B110 rule highlights that catching a broad exception without logging or handling it is considered an anti-pattern. It masks errors and can hide system degradation or security-relevant disruptions (e.g., an attacker causing faults). Proper error handling requires logging the exception at a minimum.

**Recommended Code Changes:**
Replace `pass` with a logging mechanism or specific exception handling. If the exception is genuinely expected and benign, handle the exact exception type (e.g., `except ConnectionError:`) instead of a blanket `Exception`.

Example for `test_e2e_system.py`:
```python
import logging

try:
    asyncio.run(bus.publish_state(ev, nowait=True))
except Exception as e:
    logging.debug(f"Failed to publish state: {e}")  # Handled instead of pass
```

---

## 3. Unsafe URL Open (B310: urllib urlopen)
**Location:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Severity:** Medium
**CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory - Path Traversal / SSRF potential)

**Details:**
The script uses `urllib.request.urlopen(req)` to fetch data from a URL.
Bandit raises a B310 warning because `urlopen` allows unvalidated schemes like `file://` or custom schemas. If the `url` variable is attacker-controlled, they could exploit this to read local files (Path Traversal) or conduct Server-Side Request Forgery (SSRF).

**Research:**
As detailed in security documentation (e.g., Ruff S310/Bandit B310), `urlopen` supports handlers beyond HTTP/HTTPS. Without scheme validation, an application is vulnerable to unauthorized local file access. The mitigation is to explicitly check the URL scheme before calling `urlopen`.

**Recommended Code Changes:**
Validate that the URL starts with `http://` or `https://` before opening the request. Once validated, you can suppress the Bandit warning.

```python
if not url.startswith(('http://', 'https://')):
    raise ValueError("Invalid URL scheme")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    data = json.loads(response.read().decode())
```

---
