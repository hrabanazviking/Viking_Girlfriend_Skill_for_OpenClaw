# Security Scan Report
**Date:** 2026-06-02

## Overview
A static application security testing (SAST) scan was performed using Bandit. This report outlines the discovered vulnerabilities and provides recommended code changes and research findings.

## Discovered Vulnerabilities

### B404 - blacklist
**Description:** Consider possible security implications associated with the subprocess module.
**Severity:** LOW
**Confidence:** HIGH
**More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess

**Occurrences:**
1. File: `./infra/bootstrap_host.py`, Line: 3

**Research & Recommendations:**
The `subprocess` module can be dangerous if used with untrusted input. However, if the command and arguments are hardcoded or sanitized, it is generally safe. To suppress this warning for static commands, append `# nosec B404` to the import statement.

---

### B603 - subprocess_without_shell_equals_true
**Description:** subprocess call - check for execution of untrusted input.
**Severity:** LOW
**Confidence:** HIGH
**More Info:** https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html

**Occurrences:**
1. File: `./infra/bootstrap_host.py`, Line: 15

**Research & Recommendations:**
This warning highlights `subprocess` calls without `shell=True`. While generally safer than with `shell=True`, it's still flagged for review to ensure inputs are trusted. For static or sanitized inputs, append `# nosec B603` to the line.

---

### B110 - try_except_pass
**Description:** Try, Except, Pass detected.
**Severity:** LOW
**Confidence:** HIGH
**More Info:** https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html

**Occurrences:**
1. File: `./tests/test_cove_pipeline.py`, Line: 256
2. File: `./tests/test_e2e_system.py`, Line: 169

**Research & Recommendations:**
Using `try: ... except Exception: pass` silently ignores errors, which can hide bugs and potential security issues (e.g., DoS attempts). Recommendation: Catch specific exceptions, log the error, or add `# nosec B110` if the suppression is truly intended and safe.

---

### B310 - blacklist
**Description:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
**Severity:** MEDIUM
**Confidence:** HIGH
**More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

**Occurrences:**
1. File: `./viking_girlfriend_skill/data/knowledge_reference/populate.py`, Line: 27
2. File: `./viking_girlfriend_skill/data/knowledge_reference/populate.py`, Line: 62

**Research & Recommendations:**
Using `urllib.request.urlopen` can lead to Server-Side Request Forgery (SSRF) or local file read vulnerabilities if the URL is user-controlled and the scheme (e.g., `file://`) is not validated. Recommendation: Explicitly validate the URL scheme to ensure it is `http://` or `https://` before calling `urlopen`, then append `# nosec B310` if needed.
Example Code Change:
```python
if not url.startswith(('http://', 'https://')):
    raise ValueError('Invalid URL scheme')
# nosec B310
with urllib.request.urlopen(req) as response:
    ...
```

---
