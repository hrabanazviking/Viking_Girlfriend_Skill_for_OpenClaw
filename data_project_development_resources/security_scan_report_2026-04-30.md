# Security Scan Report
**Date:** 2026-04-30

## Overview
A static application security testing (SAST) scan was performed using Bandit (version 1.9.4) on the project codebase. The scan identified several security issues with varying severity levels. As per instructions, this report outlines the discovered issues, includes relevant research, and provides recommended code changes. The codebase has not been modified; this report serves as a basis for future remediation efforts.

## Findings

### 1. High/Medium Severity: `urllib.urlopen` (B310)
**File:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Lines:** 27, 62
**Issue Text:** "Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected."
**Bandit ID:** B310
**CWE:** 22 (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'))

**Research:**
According to the [Bandit documentation for B310](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen), using `urllib.request.urlopen` without validating the URL scheme can lead to security vulnerabilities, such as Server-Side Request Forgery (SSRF) or Path Traversal attacks. If an attacker can control the URL passed to `urlopen`, they might use schemes like `file://` to read local files on the server or `ftp://` to access internal network resources.

**Recommended Code Changes:**
Before passing the URL to `urllib.request.Request` or `urllib.request.urlopen`, explicitly validate that the URL scheme is permitted (e.g., restricted to `http` or `https`). Since the URLs are constructed within the script (e.g., `url = f"https://en.wikipedia.org/..."`), the risk is relatively low, but validation is a best practice. After adding validation, append `# nosec B310` to suppress the Bandit warning.

```python
import urllib.parse

# ... inside the function where the URL is constructed ...
parsed_url = urllib.parse.urlparse(url)
if parsed_url.scheme not in ('http', 'https'):
    raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}. Only HTTP and HTTPS are allowed.")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    # ...
```

### 2. Low Severity: `import subprocess` (B404)
**File:** `./infra/bootstrap_host.py`
**Line:** 3
**Issue Text:** "Consider possible security implications associated with the subprocess module."
**Bandit ID:** B404
**CWE:** 78 (Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection'))

**Research:**
The [Bandit documentation for B404](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess) indicates that importing the `subprocess` module is flagged because its functions (like `subprocess.run`, `subprocess.Popen`) can be used to execute arbitrary system commands. If untrusted input is passed to these functions, it can result in command injection vulnerabilities.

**Recommended Code Changes:**
In `bootstrap_host.py`, the `subprocess` module is imported to check for the availability of commands like `podman`, `docker`, and `nvidia-smi`. The commands being executed are static strings defined within the code, so there is no immediate risk of command injection. To acknowledge the use of the module and suppress the warning, append `# nosec B404` to the import statement.

```python
import subprocess  # nosec B404
```

### 3. Low Severity: `subprocess.run` (B603)
**File:** `./infra/bootstrap_host.py`
**Line:** 15
**Issue Text:** "subprocess call - check for execution of untrusted input."
**Bandit ID:** B603
**CWE:** 78 (Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection'))

**Research:**
The [Bandit documentation for B603](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html) warns against using `subprocess` functions without `shell=True`. While this invocation method is safer than using a shell (which is vulnerable to shell injection attacks), it's still crucial to ensure that the input is valid and trusted. Bandit flags this to prompt developers to manually verify the input.

**Recommended Code Changes:**
In the `check_command` function, `subprocess.run` is called with a command string. Given the context (checking for hardcoded commands like `docker`), the input is controlled and safe. To suppress the warning, append `# nosec B603` to the line containing the `subprocess.run` call.

```python
def check_command(command: str) -> bool:
    """Check if a command is available on the host system."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
```

### 4. Low Severity: Use of `assert` (B101)
**Files:** Multiple files in `./tests/`
**Lines:** Various (e.g., `test_vordur_trigger.py`, `test_wyrd_vitality_modulation.py`)
**Issue Text:** "Use of assert detected. The enclosed code will be removed when compiling to optimised byte code."
**Bandit ID:** B101
**CWE:** 703 (Improper Check or Handling of Exceptional Conditions)

**Research:**
Bandit flags the use of `assert` statements because Python can be run with optimizations (the `-O` flag), which completely ignores `assert` statements. If an application relies on `assert` for critical checks (like access control or input validation), these checks will be bypassed in an optimized environment, potentially leading to security flaws.

**Recommended Code Changes:**
Since these assertions are located in test files (`./tests/`), they are used for verifying test conditions, not for enforcing application logic or security checks. It is standard practice to use `assert` in test suites (especially with `pytest`). Therefore, no code changes are necessary. These warnings can be safely ignored, or Bandit can be configured to ignore the `tests/` directory during scans.

## Conclusion
The most significant finding is the potential URL scheme vulnerability in the data population script. Implementing the recommended scheme validation and appending the appropriate `# nosec` tags will address these issues and improve the security posture of the project. No immediate action is required for the `assert` statements found in the test files.
