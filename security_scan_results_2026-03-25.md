# Security Scan Report
**Date:** 2026-03-25

## Overview
A Bandit SAST scan was performed on the `Viking_Girlfriend_Skill_for_OpenClaw` codebase on 2026-03-25. Several potential security issues were identified that require attention, including issues with the `subprocess` module, swallowed exceptions, and unsafe `urllib` usage.

---

## Detailed Findings and Recommendations

### 1. Insecure Use of `subprocess` (B404, B603)
**Severity:** LOW
**CWE:** [CWE-78: OS Command Injection](https://cwe.mitre.org/data/definitions/78.html)
**Location:**
- `infra/bootstrap_host.py`: lines 3, 15
  ```python
  14     try:
  15         subprocess.run([command, "--version"], capture_output=True, check=True)
  16         return True
  ```

**Analysis:**
The use of `subprocess` to execute commands can be vulnerable to command injection if the inputs (like `command`) are untrusted or maliciously manipulated. While `shell=False` is inherently safer as it doesn't invoke a shell, the input command should still be validated to ensure it's a safe and expected executable path.

**Recommendation:**
- Validate the `command` argument against a strict allowlist of permitted commands (e.g., `['podman', 'docker', 'nvidia-smi']`) before calling `subprocess.run()`.

---

### 2. Silently Swallowing Exceptions (B110)
**Severity:** LOW
**CWE:** [CWE-703: Improper Check or Handling of Exceptional Conditions](https://cwe.mitre.org/data/definitions/703.html)
**Locations:**
- `tests/test_cove_pipeline.py`: lines 256-257
  ```python
  255             cove._cb_pipeline.on_failure(RuntimeError("test failure"))
  256         except Exception:
  257             pass
  ```
- `tests/test_e2e_system.py`: lines 169-170
  ```python
  168             asyncio.run(bus.publish_state(ev, nowait=True))
  169         except Exception:
  170             pass  # offline / loop not running — acceptable
  ```

**Analysis:**
Using `try: ... except Exception: pass` silently ignores errors. This pattern makes debugging difficult, as it hides runtime failures and potential state corruption. It can also unexpectedly catch system-exiting exceptions like `KeyboardInterrupt` if not careful, though `Exception` usually spares them compared to a bare `except:`.

**Recommendation:**
- Replace `pass` with explicit logging using `logger.warning("Reason for failure: %s", e)`.
- If the exception is truly expected and safe to ignore in testing, document it clearly, or catch only the specific exception types expected.

---

### 3. Unvalidated Scheme in `urllib.request.urlopen` (B310)
**Severity:** MEDIUM
**CWE:** [CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')](https://cwe.mitre.org/data/definitions/22.html) / Server-Side Request Forgery (SSRF)
**Locations:**
- `viking_girlfriend_skill/data/knowledge_reference/populate.py`: lines 27, 62
  ```python
  26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  27                 with urllib.request.urlopen(req) as response:
  ```

**Analysis:**
The `urllib.request.urlopen` function is capable of opening `file://` and `ftp://` URLs in addition to HTTP/HTTPS. If an attacker can manipulate the `url` parameter, they could potentially read local files on the system or access internal network resources (SSRF).

**Recommendation:**
- Add explicit validation to ensure the URL starts with `https://` or `http://` before invoking `urlopen`.
  ```python
  if not url.lower().startswith(('http://', 'https://')):
      raise ValueError("Invalid URL scheme")
  req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  with urllib.request.urlopen(req) as response:
      ...
  ```
