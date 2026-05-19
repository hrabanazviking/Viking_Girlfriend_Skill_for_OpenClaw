# Security Scan Report: 2026-03-27

## Overview
A comprehensive static analysis security scan was performed on the codebase using [Bandit](https://github.com/PyCQA/bandit). The scan identified several potential vulnerabilities related to OS command injection (CWE-78), path traversal/URL scheme manipulation (CWE-22), and improper exception handling (CWE-703).

This document outlines the findings, provides context from security research, and recommends code changes to mitigate these risks.

---

## Findings and Recommendations

### 1. CWE-78: OS Command Injection via `subprocess.run`

**Locations:**
*   `infra/bootstrap_host.py:3`
*   `infra/bootstrap_host.py:15`

**Issue Description:**
Bandit reported warnings regarding the use of the `subprocess` module. Specifically, in `infra/bootstrap_host.py`, the `check_command` function uses `subprocess.run` with a dynamically constructed command list where the executable itself is a variable argument.
```python
def check_command(command: str) -> bool:
    """Check if a command is available on the host system."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
```

**Research & Impact:**
While the current implementation is not technically vulnerable to shell injection because `shell=True` is not used and the arguments are passed as a list, dynamically determining the executable path based on user input or external variables is generally considered a bad practice. An attacker could potentially manipulate the environment to execute a malicious binary if the path is not absolute or securely resolved.

Furthermore, using `subprocess.run` simply to check if a command exists is inefficient, as it spawns a full sub-process and executes the binary. As discussed on [StackOverflow](https://stackoverflow.com/questions/43905907/python-should-i-use-shutil-or-subprocess-to-manipulate-files-and-directories-as), using the built-in `shutil` module is much faster and avoids the risks associated with process execution.

**Recommended Code Change:**
Refactor the `check_command` function to use `shutil.which()`, which safely checks the system's `PATH` for the executable without running it.

```python
import shutil

def check_command(command: str) -> bool:
    """Check if a command is available on the host system."""
    return shutil.which(command) is not None
```

---

### 2. CWE-22: Path Traversal and URL Scheme Manipulation

**Locations:**
*   `viking_girlfriend_skill/data/knowledge_reference/populate.py:27`
*   `viking_girlfriend_skill/data/knowledge_reference/populate.py:62`

**Issue Description:**
Bandit flagged the use of `urllib.request.urlopen(req)` because the URL is dynamically constructed. The scanner warns: *"Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected."*

**Research & Impact:**
The `urllib.request.urlopen` function is highly permissive. By default, it supports multiple URL schemes, including `http://`, `https://`, `ftp://`, and critically, `file://`. If an attacker can manipulate the input that constructs the URL (e.g., the `current_cat` or `titles_param` variables in the script), they could potentially supply a `file://` URI to read arbitrary local files from the server's filesystem. This is a classic form of Local File Inclusion (LFI) or Path Traversal, often classified under CWE-22 or CWE-73 (External Control of File Name or Path).
Documentation from sources like [Bandit's B310 Rule](https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b310-urllib-urlopen) explicitly highlights this risk.

**Recommended Code Change:**
Before opening the URL, explicitly validate that the URL strictly uses the `https://` scheme.

```python
# Apply this validation before calling urllib.request.urlopen in both locations
if not url.startswith("https://"):
    raise ValueError("Invalid URL scheme. Only https:// is permitted.")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    # ... process response ...
```
Alternatively, migrating to the popular `requests` library is often recommended for a safer, higher-level HTTP client interface, but the above validation is a sufficient fix for the current implementation.

---

### 3. CWE-703: Improper Check for Unusual or Exceptional Conditions

**Locations:**
*   `tests/test_cove_pipeline.py:256`
*   `tests/test_e2e_system.py:169`

**Issue Description:**
Bandit identified instances of the "Try, Except, Pass" anti-pattern in the test files:
```python
        try:
            cove._cb_pipeline.on_failure(RuntimeError("test failure"))
        except Exception:
            pass
```

**Research & Impact:**
According to [Ruff (S110)](https://docs.astral.sh/ruff/rules/try-except-pass/) and general secure coding practices, catching the broad `Exception` class and silently passing (`pass`) is dangerous. It suppresses all errors, which can hide critical bugs, system failures, or even security-relevant events like authentication failures or denial-of-service conditions. This makes debugging significantly harder and can obscure malicious activity from logs.

While these instances are in the test suite and not production code, it is still a poor practice that can lead to flaky tests or mask actual regressions in the code being tested.

**Recommended Code Change:**
Instead of silently passing, log the exception or catch only the specific exception types that are expected to fail during the test.

```python
# Recommended fix for tests/test_cove_pipeline.py
import logging
logger = logging.getLogger(__name__)

        try:
            cove._cb_pipeline.on_failure(RuntimeError("test failure"))
        except Exception as e:
            logger.debug(f"Expected failure in test: {e}")

# Recommended fix for tests/test_e2e_system.py
# (It already has a comment `# offline / loop not running — acceptable`, but it should log or catch specific errors)
        try:
            import asyncio
            asyncio.run(bus.publish_state(ev, nowait=True))
        except RuntimeError: # Catch specific asyncio errors if expected
            pass # Or better: logger.debug("Event loop not running, skipping state publish in test")
        except Exception as e:
            logger.warning(f"Unexpected error in test publish_state: {e}")
```
