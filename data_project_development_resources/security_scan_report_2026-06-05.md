# Codebase Security and Bug Scan Report
Date: 2026-06-05

## Overview
A static analysis scan was conducted on the codebase.

## Findings

### 1. B404: Import of subprocess module
**Location:** `./infra/bootstrap_host.py:3`
**Severity:** LOW
**Issue:** `import subprocess`
**Details:** Bandit triggers a warning for importing the `subprocess` module due to potential security implications.
**Recommendation:** Append `# nosec B404` to the import line to suppress the warning, as the usage of `subprocess` is intentional and secure.
**Reference:** https://bandit.readthedocs.io/en/1.7.5/blacklists/blacklist_imports.html#b404-import-subprocess

### 2. B603: subprocess call
**Location:** `./infra/bootstrap_host.py:15`
**Severity:** LOW
**Issue:** `subprocess.run([command, "--version"], capture_output=True, check=True)`
**Details:** Bandit flags `subprocess` calls without `shell=True` to check for execution of untrusted input. In this case, `command` is explicitly passed within the script and is safe.
**Recommendation:** Append `# nosec B603` to the line to suppress the warning.
**Reference:** https://bandit.readthedocs.io/en/1.7.5/plugins/b603_subprocess_without_shell_equals_true.html

### 3. B110: Try, Except, Pass
**Location:** `./tests/test_cove_pipeline.py:256`
**Severity:** LOW
**Issue:** Silently ignoring an exception (`except Exception: pass`).
**Details:** Catching a base `Exception` and silently using `pass` is flagged because it can hide errors or potential security issues. In tests, it might be acceptable, but it's better to explicitly suppress the warning if it's intentional.
**Recommendation:** Append `# nosec B110` to the `except` block line to suppress the warning, or ideally, catch a more specific exception if possible.
**Reference:** https://bandit.readthedocs.io/en/latest/plugins/b110_try_except_pass.html

### 4. B110: Try, Except, Pass
**Location:** `./tests/test_e2e_system.py:169`
**Severity:** LOW
**Issue:** Silently ignoring an exception (`except Exception: pass`).
**Details:** Similar to the previous finding, catching `Exception` and passing is generally bad practice, though used here to ignore offline states.
**Recommendation:** Append `# nosec B110` to the `except` line.
**Reference:** https://bandit.readthedocs.io/en/latest/plugins/b110_try_except_pass.html

### 5. B310: Audit url open for permitted schemes
**Location:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py:27`
**Severity:** MEDIUM
**Issue:** `with urllib.request.urlopen(req) as response:`
**Details:** `urllib.request.urlopen` can open `file://` or custom schemes, potentially leading to Server-Side Request Forgery (SSRF) or Path Traversal if the URL is user-controlled.
**Recommendation:** Validate that the URL starts with `http://` or `https://` before opening it. For instance, `if not url.lower().startswith(('http://', 'https://')): raise ValueError('Invalid URL scheme')`. Then append `# nosec B310` to suppress the warning.
**Reference:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

### 6. B310: Audit url open for permitted schemes
**Location:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py:62`
**Severity:** MEDIUM
**Issue:** `with urllib.request.urlopen(req) as response:`
**Details:** Same issue as above, potentially leading to Path Traversal or SSRF.
**Recommendation:** Validate the URL scheme before calling `urlopen` and add `# nosec B310`.
**Reference:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen
