# Security Scan Report: 2026-05-12

## Overview

A static application security testing (SAST) scan was performed using Bandit. Several low-to-medium severity vulnerabilities were detected in the codebase. This report details the findings, provides background research on the issues, and offers recommended code changes for remediation. Note that this report is strictly observational; no code fixes have been automatically applied.

## Findings

### 1. Issue: `subprocess` Usage (Bandit B404 & B603)
* **Locations:**
  * `./infra/bootstrap_host.py:3` (B404)
  * `./infra/bootstrap_host.py:15` (B603)
* **Description:**
  * The `subprocess` module is imported and used. While this module is necessary for invoking external executables, it carries potential security risks if user-provided input is not properly sanitized (Command Injection).
  * Specifically, Bandit B603 warns about the use of `subprocess` without `shell=True`, which is safer than using the shell, but still requires validation of arguments.
* **Research & Context:**
  * Bandit B603 Documentation: [https://bandit.readthedocs.io/en/latest/plugins/b603_subprocess_without_shell_equals_true.html](https://bandit.readthedocs.io/en/latest/plugins/b603_subprocess_without_shell_equals_true.html)
  * Bandit B404 Documentation: [https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html)
  * In the codebase, `subprocess.run([command, "--version"], capture_output=True, check=True)` is used where `command` is explicitly provided by the system.
* **Recommended Code Changes:**
  * Since the commands (`podman`, `docker`, `nvidia-smi`) are hardcoded internal strings and not derived from untrusted user input, the usage is safe.
  * To resolve the Bandit warning without changing functionality, use the `# nosec` directive to explicitly acknowledge the manual review:
    ```python
    import subprocess  # nosec B404
    # ...
    subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
    ```

### 2. Issue: `try-except-pass` Detected (Bandit B110)
* **Locations:**
  * `./tests/test_cove_pipeline.py:256`
  * `./tests/test_e2e_system.py:169`
* **Description:**
  * A broad `try-except` block catches an `Exception` (or all exceptions) and silently passes without handling or logging it.
  * This is considered bad practice because it can hide unexpected errors, making debugging difficult and potentially masking malicious activities or denial-of-service attempts.
* **Research & Context:**
  * Bandit B110 Documentation: [https://bandit.readthedocs.io/en/latest/plugins/b110_try_except_pass.html](https://bandit.readthedocs.io/en/latest/plugins/b110_try_except_pass.html)
* **Recommended Code Changes:**
  * If the intention is to ignore a specific expected error, the exception type should be as narrow as possible. For testing purposes, if ignoring is truly desired, logging or capturing the exact expected error type is preferred.
  * Example fix for `test_cove_pipeline.py`:
    ```python
    try:
        cove._cb_pipeline.on_failure(RuntimeError("test failure"))
    except RuntimeError: # Or the specific exception type thrown
        pass
    ```
    If `Exception` is specifically intended to be ignored, logging can be added, or the `# nosec B110` directive can be used if it's strictly a testing artifact.

### 3. Issue: Audit `urllib.urlopen` for Permitted Schemes (Bandit B310)
* **Locations:**
  * `./viking_girlfriend_skill/data/knowledge_reference/populate.py:27`
  * `./viking_girlfriend_skill/data/knowledge_reference/populate.py:62`
* **Description:**
  * The `urllib.request.urlopen` function is used. Allowing arbitrary URLs can lead to Server-Side Request Forgery (SSRF) or unexpected file access if schemes like `file://` are passed.
* **Research & Context:**
  * Bandit B310 Documentation: [https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html](https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html)
* **Recommended Code Changes:**
  * Explicitly validate the URL scheme before calling `urlopen`. Ensure the URL starts with `http://` or `https://`.
  * After validation, the `# nosec B310` comment can be added.
  * Example fix:
    ```python
    if not url.startswith(('http://', 'https://')):
        raise ValueError("Invalid URL scheme")
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response: # nosec B310
        # ...
    ```
