# Security Scan Report & Mitigation Guide

**Date:** 2026-04-22

## Overview

A security scan using `bandit` was performed across the codebase to identify potential vulnerabilities. The scan highlighted a few specific issues that have now been addressed.

## Findings & Mitigations

### 1. B310: `urllib_urlopen`
*   **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
*   **Severity:** Medium
*   **Description:** The scan flagged the use of `urllib.request.urlopen`. Allowing the use of `file://` or custom schemes when opening URLs dynamically can lead to Server-Side Request Forgery (SSRF) or local file read vulnerabilities.
*   **Research:** According to Bandit documentation, auditing URL open for permitted schemes is necessary. An attacker might manipulate a URL to point to internal services or local files if input is untrusted.
*   **Mitigation:**
    *   **Recommended Change:** Validate the URL schema explicitly before making the request.
    *   **Implemented Change:** Added a check `if not url.startswith('https://en.wikipedia.org/'): raise ValueError('Invalid URL schema')` before the `urlopen` call to restrict requests strictly to the intended Wikipedia API. The `urlopen` calls were then appended with `# nosec B310` to suppress the Bandit warning since the input is now safely constrained.

### 2. B404: `import_subprocess`
*   **File:** `infra/bootstrap_host.py`
*   **Severity:** Low
*   **Description:** Importing the `subprocess` module is inherently risky as it allows execution of external commands. Bandit flags this to prompt a manual review.
*   **Research:** Python's `subprocess` module, if not handled carefully, can execute arbitrary commands on the host OS. This check encourages developers to review *how* `subprocess` is used in the module.
*   **Mitigation:**
    *   **Recommended Change:** Review the module to ensure no untrusted input is passed to subprocess functions. Once verified, the import can be marked safe.
    *   **Implemented Change:** Reviewed the file and confirmed that `subprocess` is only used with hardcoded commands (`podman`, `docker`, `nvidia-smi`). Appended `# nosec B404` to `import subprocess`.

### 3. B603: `subprocess_without_shell_equals_true`
*   **File:** `infra/bootstrap_host.py`
*   **Severity:** Low
*   **Description:** The scan found a call to `subprocess.run` where `shell=False` (default). While this avoids shell injection vulnerabilities (unlike `shell=True`), there is still a risk if user-provided input is passed as arguments to the executable.
*   **Research:** Bandit warns that even without a shell, invoking executables requires care to sanitize any user-provided or variable input. The specific CWE is CWE-78 (OS Command Injection).
*   **Mitigation:**
    *   **Recommended Change:** Ensure the command and arguments passed to `subprocess.run` are safe, static, or thoroughly sanitized.
    *   **Implemented Change:** The inputs to `check_command` in `verify_host()` are hardcoded strings. Thus, no injection is possible. Appended `# nosec B603` to the `subprocess.run` line.

## Conclusion

The identified security concerns were relatively low risk due to the context of their usage (hardcoded values and internal scripting), but they have been proactively mitigated using proper validation and explicit security markers (`# nosec`) to satisfy static analysis tools and establish a secure coding standard.
