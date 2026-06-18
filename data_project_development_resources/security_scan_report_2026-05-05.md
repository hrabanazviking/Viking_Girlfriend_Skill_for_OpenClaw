# Security Scan Report

**Date:** 2026-05-05
**Tool Used:** Bandit (Static Application Security Testing)

## Overview
A comprehensive static security scan was performed across the codebase using Bandit. The scan identified several potential vulnerabilities that require attention.

## Findings

### 1. B310: Insecure Use of `urllib.urlopen`
- **Location:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Severity:** Medium
- **Confidence:** High
- **Description:** The `urllib.request.urlopen` function is used to open URLs without prior validation of the URL scheme.
- **Vulnerability Context (Research):** `urllib` can open not only `http://` and `https://` URLs, but also `ftp://` and `file://`. If the URL is controllable by an external user, this can lead to Server-Side Request Forgery (SSRF) or Local File Inclusion/Path Traversal. An attacker might be able to read sensitive local files (e.g., `file:///etc/passwd`) or make requests to internal network resources.
- **Recommended Fix:** Ensure the URL scheme is explicitly validated before calling `urlopen`.
  ```python
  if url.lower().startswith('http://') or url.lower().startswith('https://'):
      req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
      with urllib.request.urlopen(req) as response:
          # ...
  else:
      raise ValueError("Invalid URL scheme")
  ```

### 2. B404 and B603: Potential Subprocess Injection
- **Location:** `infra/bootstrap_host.py`
- **Severity:** Low
- **Confidence:** High
- **Description:** The `subprocess` module is imported (B404), and `subprocess.run` is called without `shell=True` (B603).
- **Vulnerability Context (Research):** The `subprocess` module allows the execution of external commands. B404 is a general warning about importing `subprocess`. B603 flags usage where inputs to the subprocess call might not be properly sanitized. In `bootstrap_host.py`, `subprocess.run` is used to check if commands (like `docker`, `podman`, `nvidia-smi`) exist. While passing a list of arguments (without `shell=True`) is generally safer than passing a single string, it can still be vulnerable if the command string itself is derived from untrusted input.
- **Recommended Fix:** In this specific case, the commands being checked are statically defined and safe. To resolve the Bandit warnings, append `# nosec B404` to the import statement and `# nosec B603` to the `subprocess.run` call.
  ```python
  import subprocess  # nosec B404
  # ...
  subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
  ```

### 3. B101: Use of `assert`
- **Location:** Multiple test files in `research_data/tests/` and `tests/`.
- **Severity:** Low
- **Confidence:** High
- **Description:** The `assert` statement is used extensively throughout the test files.
- **Vulnerability Context (Research):** In Python, `assert` statements are removed when the code is compiled to optimized byte code (using the `-O` flag). If `assert` is used in production code for input validation or security checks, those checks will be bypassed in optimized mode.
- **Recommended Fix:** The use of `assert` in test files (specifically those run via `pytest`) is standard practice and generally acceptable. No code changes are required for the test files. However, it's crucial to ensure `assert` is not used for critical security checks or logic flow in the main application code (`viking_girlfriend_skill/scripts/`, etc.). If tests are run directly (not via `pytest`), exceptions like `ValueError` or `AssertionError` should be explicitly raised instead.
