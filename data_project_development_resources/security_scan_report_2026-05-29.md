# Security and Bug Scan Report (2026-05-29)

## Executive Summary
A static analysis of the codebase was performed using `bandit` and `flake8`. Several security and linting issues were identified, which should be addressed to improve code quality and security.

## Findings from Bandit
The Bandit scan identified several security warnings (filtering out `B101: assert_used` as per project memory instructions).

### 1. B404: Import subprocess and B603: subprocess_without_shell_equals_true
**File:** `./infra/bootstrap_host.py`
**Lines:** 3, 15
**Details:** The `subprocess` module is imported and used. While `shell=True` is not used (which is good), it's generally recommended to be cautious with subprocesses, ensuring input is sanitized and not untrusted.
**Research (CWE-78):** According to https://cwe.mitre.org/data/definitions/78.html (Improper Neutralization of Special Elements used in an OS Command), OS Command Injection occurs when an application constructs all or part of an OS command using externally-influenced input but does not neutralize special elements. When using subprocess, passing arguments as a list of strings is best, which is already done here (`subprocess.run([command, "--version"], capture_output=True, check=True)`).
**Recommended Fix:** As per memory instructions, if using static or hardcoded commands with `subprocess`, append `# nosec B404` to the import and `# nosec B603` to the call to suppress these warnings.
```python
import subprocess # nosec B404
...
subprocess.run([command, "--version"], capture_output=True, check=True) # nosec B603
```

### 2. B110: try_except_pass
**File:** `./tests/test_cove_pipeline.py` (Lines 256-257) and `./tests/test_e2e_system.py` (Lines 169-170)
**Details:** The code uses `try...except Exception: pass`, which silently ignores all exceptions. This is generally an anti-pattern as it can hide unexpected errors.
**Research (CWE-703):** According to https://cwe.mitre.org/data/definitions/703.html (Improper Check or Handling of Exceptional Conditions), the product does not properly anticipate or handle exceptional conditions that rarely occur during normal operation. Catching `Exception` and doing nothing can mask critical bugs.
**Recommended Fix:** While acceptable in some specific test setups, it's better to catch specific exceptions or log them. If ignoring is truly intended, document it clearly, or log the error at a debug level.

### 3. B310: urllib_urlopen
**File:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Lines:** 27, 62
**Details:** The code uses `urllib.request.urlopen` which can be exploited for Server-Side Request Forgery (SSRF) or Path Traversal if the URL scheme is not restricted (e.g., allowing `file://`).
**Research (CWE-22):** According to https://cwe.mitre.org/data/definitions/22.html (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')), by using special elements such as `..` and `/` separators, attackers can escape outside of the restricted location to access files or directories elsewhere on the system. `urllib.urlopen` can open local files if the scheme is `file://`.
**Recommended Fix:** Explicitly validate the URL scheme (ensuring it starts with `http://` or `https://`) before appending `# nosec B310` to suppress Bandit warnings, as per memory instructions.
```python
if not url.startswith(('http://', 'https://')):
    raise ValueError("Invalid URL scheme")
with urllib.request.urlopen(req) as response: # nosec B310
    ...
```

## Findings from Flake8
The Flake8 scan generated many output lines (over 7000 warnings/errors), predominantly regarding style (e.g., line too long, imported but unused). There are some critical parsing errors:

### E999 IndentationError / SyntaxError
**Files:**
- `./scripts/gen_warfare.py:45:11: E999 IndentationError: unindent does not match any outer indentation level`
- Several other scripts under `./scripts/` (e.g., `write_archaeology_1.py`, `write_archaeology_2.py`) were flagged by Bandit for syntax errors while parsing AST, which likely corresponds to similar parsing issues.
**Recommended Fix:** Review and correct the indentation and syntax in these scripts.

### F401: imported but unused
**Files:** Various files, notably `./infra/bootstrap_host.py`, `./ops/launch_calibration.py`, and many `./scripts/*.py` files.
**Recommended Fix:** Remove unused imports to clean up the code.
