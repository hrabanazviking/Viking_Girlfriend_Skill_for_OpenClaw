# Bug and Security Scan Report - 2026-05-14

This document outlines the findings of a comprehensive code audit encompassing static security scanning (Bandit), code quality checks (Flake8, Pylint), and type checking (MyPy).

## 1. Security Vulnerabilities (Bandit)

Bandit scanning revealed several issues that require attention.

### 1.1. B310: Audit url open for permitted schemes
**Severity:** Medium
**Confidence:** High
**Files Affected:**
* `viking_girlfriend_skill/data/knowledge_reference/populate.py` (lines 27, 62)
    ```python
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())
    ```

**Research & Implications:**
According to [DeepSource](https://deepsource.com/directory/python/issues/BAN-B310), `urllib` not only opens `http://` or `https://` URLs, but also `ftp://` and `file://`. If a user can manipulate the URL passed to `urlopen`, they could potentially access local files on the system or access internal network resources. This makes the application vulnerable to Server-Side Request Forgery (SSRF) and path traversal attacks (CWE-22 / CWE-918).

**Recommended Code Changes:**
Ensure the URL starts with a permitted scheme before passing it to `urlopen`.

```python
<<<<<<< SEARCH
        req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
=======
        # Validate URL scheme to prevent SSRF/Path Traversal
        if not url.lower().startswith(('http://', 'https://')):
            raise ValueError(f"Invalid URL scheme: {url}")
        req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
        with urllib.request.urlopen(req) as response: # nosec B310
            data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

### 1.2. B603: subprocess_without_shell_equals_true
**Severity:** Low
**Confidence:** High
**Files Affected:**
* `infra/bootstrap_host.py` (line 15)
    ```python
    subprocess.run([command, "--version"], capture_output=True, check=True)
    ```

**Research & Implications:**
The [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html) specifies that while using `subprocess` without `shell=True` is not vulnerable to typical shell injection, it may still present a security issue if the input being executed is user-controlled (CWE-78). In this specific file, the `command` variable is passed directly into `subprocess.run`. If `command` isn't strictly validated or hardcoded, malicious input could execute arbitrary binaries.

**Recommended Code Changes:**
If the command is known to be static or safe, validate it against a whitelist, or simply suppress the warning if it's confirmed safe contextually.

```python
<<<<<<< SEARCH
def check_command(command: str) -> bool:
    """Check if a command is available on the host system."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
=======
def check_command(command: str) -> bool:
    """Check if a command is available on the host system."""
    # Validate command is safe to run
    allowed_commands = ["podman", "docker", "nvidia-smi"]
    if command not in allowed_commands:
        return False
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True) # nosec B603
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
>>>>>>> REPLACE
```

### 1.3. B404: import_subprocess
**Severity:** Low
**Confidence:** High
**Files Affected:**
* `infra/bootstrap_host.py` (line 3)

**Research & Implications:**
The [Bandit Blacklist](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess) flags the `subprocess` module itself because of the potential security implications of spawning new processes. This is a generic warning.

**Recommended Code Changes:**
Suppress the warning by adding `# nosec B404` to the import statement if the use of `subprocess` has been audited and deemed necessary.

```python
<<<<<<< SEARCH
import sys
import subprocess
import platform
=======
import sys
import subprocess # nosec B404
import platform
>>>>>>> REPLACE
```

### 1.4. B110: try_except_pass
**Severity:** Low
**Confidence:** High
**Files Affected:**
* `tests/test_cove_pipeline.py` (line 256)
* `tests/test_e2e_system.py` (line 169)
    ```python
    except Exception:
        pass
    ```

**Research & Implications:**
According to the [Bandit Documentation](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html), catching an exception and silently ignoring it (CWE-703) is bad practice. It can mask errors, including potential security issues where an attacker is attempting to disrupt a service. Errors should at least be logged. If ignoring the error is truly intended, catching a specific exception type (like `ValueError`) instead of the base `Exception` is preferred.

**Recommended Code Changes:**
Replace `pass` with a logging statement, or catch a more specific exception if possible. Alternatively, suppress with `# nosec B110` if it's acceptable in tests.

## 2. Code Quality and Typing Issues

### 2.1 Flake8 Findings
Flake8 identified a large number of issues (7401).

* **E999 IndentationError:**
    There are several critical syntax errors across multiple generated script files (`scripts/gen_warfare.py`, `scripts/write_archaeology_*.py`, `scripts/write_arts_*.py`, etc.) where unindentation does not match any outer indentation level. These scripts currently cannot be parsed or executed by Python.
    *Recommended Change:* Fix the indentation in these scripts.

* **F401 '...' imported but unused / F841 local variable '...' is assigned to but never used:**
    Many files have unused imports and variables, leading to clutter.
    *Recommended Change:* Remove unused imports and variables to clean up the code.

### 2.2 Pylint Findings
Pylint reported 2956 issues. The most common issues include:
* `C0116: Missing function or method docstring`
* `W0212: Access to a protected member _... of a client class`
* `W0718: Catching too general exception Exception`
* `C0301: Line too long`
* `C0415: Import outside toplevel`
* `E0401: Unable to import 'pytest'` (in test files), indicating potential environment pathing issues when pylint is run.

*Recommended Change:* Run an automated formatter (like `black` or `autopep8`) and address docstrings and overly broad exception catching.

### 2.3 MyPy Findings
MyPy successfully ran but hit a blocking syntax error early in the execution:
* `scripts/gen_warfare.py:45: error: Unindent does not match any outer indentation level [syntax]`
Because of this error, MyPy prevented further type checking across the project.
*Recommended Change:* Fix the IndentationError in `scripts/gen_warfare.py` and re-run MyPy to discover underlying typing issues.
