# Codebase Security Scan Report

**Date:** 2026-04-26

## Overview

A comprehensive security scan of the codebase was conducted using `bandit`, a Static Application Security Testing (SAST) tool for Python. The scan identified a few potential vulnerabilities and bad practices that should be addressed.

## Findings and Recommendations

### 1. Subprocess Execution of Untrusted Input (B404 & B603)
* **Locations:**
  * `infra/bootstrap_host.py` (Line 3, Line 15)
* **Severity:** Low
* **Description:** The `subprocess` module is used to invoke external commands (`podman`, `docker`, `nvidia-smi`). Bandit flags any use of `subprocess` as a potential risk (B404) and specifically flags `subprocess.run` (B603) because executing untrusted input can lead to shell injection vulnerabilities (CWE-78).
* **Research Data:** According to Bandit documentation (https://bandit.readthedocs.io/en/latest/plugins/b603_subprocess_without_shell_equals_true.html), invoking commands without a shell (`shell=False`, the default) is generally safer but still flagged. Because the commands used in `bootstrap_host.py` are hardcoded/static and do not use untrusted user input, this is a false positive.
* **Recommended Change:** Append `# nosec B404` to the import statement and `# nosec B603` to the `subprocess.run` call to suppress these warnings since the usage is verified as safe.

### 2. Insecure URL Open Scheme (B310)
* **Locations:**
  * `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line 27, Line 62)
* **Severity:** Medium
* **Description:** The `urllib.request.urlopen` function is used without validating the URL scheme. If an attacker can manipulate the URL, they could use schemes like `file://` to read local files on the server or `ftp://` to access internal network resources.
* **Research Data:** According to DeepSource (https://deepsource.com/directory/python/issues/BAN-B310), this vulnerability can lead to Server Side Request Forgery (SSRF) and is tracked as CWE-918. It is highly recommended to validate user-provided data, such as URLs, before opening them.
* **Recommended Change:** Explicitly validate the URL scheme before calling `urlopen`. For example, add a check: `if not url.lower().startswith(('http://', 'https://')):` and raise an error or handle it appropriately. After validating the scheme, `# nosec B310` can be used.

### 3. Try-Except-Pass Detected (B110)
* **Locations:**
  * `tests/test_cove_pipeline.py` (Line 256)
  * `tests/test_e2e_system.py` (Line 169)
* **Severity:** Low
* **Description:** The tests contain `try` blocks that catch all exceptions (`except Exception:`) and silently ignore them using `pass`.
* **Research Data:** According to Bandit documentation (https://bandit.readthedocs.io/en/latest/plugins/b110_try_except_pass.html), this is considered a bad practice (CWE-703) because it can suppress critical exceptions, making debugging difficult. It can also mask attempts to disrupt a service by causing a large volume of errors.
* **Recommended Change:** Instead of a bare `except` or catching all exceptions and doing nothing, it is recommended to either specify the exact exception type expected (e.g., `except FileNotFoundError: pass`) or log the error so that the failure is not completely silent.
