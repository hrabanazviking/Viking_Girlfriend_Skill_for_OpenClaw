# Security Scan Report - 2026-06-07

This report contains the findings of a Bandit static security scan performed on the codebase. It details identified vulnerabilities, explanations of the underlying issues based on research, and recommended code changes to address them.

## Issue Type: B404: blacklist

### Vulnerability Description
The Bandit B404 rule highlights the importation of the `subprocess` module. The `subprocess` module is extremely powerful and allows running external commands. However, improper usage, particularly when user-supplied input is involved, can lead to Command Injection vulnerabilities. If an attacker can control part of the command string passed to functions like `subprocess.run`, `subprocess.Popen`, or `subprocess.call` (especially when `shell=True`), they may be able to execute arbitrary commands on the host operating system with the privileges of the Python process.

### Occurrences
- **File:** `./infra/bootstrap_host.py`
- **Line:** `3`
- **Severity:** `LOW`
- **Confidence:** `HIGH`
- **Code Snippet:**
```python
2 import sys
3 import subprocess
4 import platform
```

### Recommended Changes
In the context of `infra/bootstrap_host.py`, the `subprocess` module is required for checking if commands like 'podman', 'docker', or 'nvidia-smi' are installed. Since the commands are hardcoded in the script and not derived from untrusted user input, the risk of command injection is minimal. However, to explicitly declare this usage as intentional and reviewed, and to clear the Bandit finding, it is recommended to add a `# nosec B404` comment to the import line.

**Suggested Code Update in `infra/bootstrap_host.py`:**
```python
import sys
import subprocess  # nosec B404
import platform
```

## Issue Type: B603: subprocess_without_shell_equals_true

### Vulnerability Description
The Bandit B603 rule flags instances where `subprocess` functions are called with `shell=False` (which is often the default or implied). While `shell=False` is safer than `shell=True` because it bypasses the shell's parsing and prevents many types of injection, Bandit still issues a low-severity warning. This is because the arguments passed to the executed program could still potentially be malicious if derived from untrusted input. Bandit acts as a simple linter here; it sees a variable being passed as an argument but cannot perform data flow analysis to determine if that variable is safe.

### Occurrences
- **File:** `./infra/bootstrap_host.py`
- **Line:** `15`
- **Severity:** `LOW`
- **Confidence:** `HIGH`
- **Code Snippet:**
```python
14     try:
15         subprocess.run([command, "--version"], capture_output=True, check=True)
16         return True
```

### Recommended Changes
In `infra/bootstrap_host.py`, the `command` variable passed to `subprocess.run` comes from hardcoded strings within the script (e.g., "podman", "docker", "nvidia-smi"). Therefore, it is safe from external injection. To acknowledge the review and suppress the warning, append `# nosec B603` to the specific line.

**Suggested Code Update in `infra/bootstrap_host.py`:**
```python
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
        return True
```

## Issue Type: B110: try_except_pass

### Vulnerability Description
The Bandit B110 rule detects `try`-`except`-`pass` blocks, also known as 'silenced exceptions'. Catching a broad exception like `Exception` and doing nothing (`pass`) can hide bugs, making debugging difficult. More importantly, in certain contexts, silencing exceptions can mask security-related failures, such as authorization checks or input validation errors, potentially allowing an application to proceed in an insecure state.

### Occurrences
- **File:** `./tests/test_cove_pipeline.py`
- **Line:** `256`
- **Severity:** `LOW`
- **Confidence:** `HIGH`
- **Code Snippet:**
```python
255             cove._cb_pipeline.on_failure(RuntimeError("test failure"))
256         except Exception:
257             pass
258
```
- **File:** `./tests/test_e2e_system.py`
- **Line:** `169`
- **Severity:** `LOW`
- **Confidence:** `HIGH`
- **Code Snippet:**
```python
168             asyncio.run(bus.publish_state(ev, nowait=True))
169         except Exception:
170             pass  # offline / loop not running — acceptable
171
```

### Recommended Changes
The instances flagged are within test files (`tests/test_cove_pipeline.py` and `tests/test_e2e_system.py`). In testing contexts, particularly when intentionally verifying failure scenarios or tearing down async loops, it might be acceptable to catch and pass on specific exceptions. To properly address these warnings while preserving the test intent, add `# nosec B110` to the `except` blocks. Alternatively, replacing `pass` with a logging statement or catching a more specific exception type is good practice, but the `# nosec` directive is the standard way to clear the SAST finding when the behavior is explicitly desired.

**Suggested Code Updates:**

**In `tests/test_cove_pipeline.py`:**
```python
        except Exception:  # nosec B110
            pass
```

**In `tests/test_e2e_system.py`:**
```python
        except Exception:  # nosec B110
            pass  # offline / loop not running — acceptable
```

## Issue Type: B310: blacklist

### Vulnerability Description
The Bandit B310 rule checks for the usage of `urllib.request.urlopen` (or similar functions). These functions open URLs provided as arguments. The primary security concern is Server-Side Request Forgery (SSRF) and Path Traversal. If an application accepts a URL from an untrusted source and opens it using `urlopen` without validation, an attacker might provide a URL with a local file scheme (e.g., `file:///etc/passwd`) to read local files on the server. Alternatively, they might provide a URL pointing to an internal service (e.g., `http://localhost:8080/admin`), forcing the server to make unauthorized requests on their behalf.

### Occurrences
- **File:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line:** `27`
- **Severity:** `MEDIUM`
- **Confidence:** `HIGH`
- **Code Snippet:**
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```
- **File:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line:** `62`
- **Severity:** `MEDIUM`
- **Confidence:** `HIGH`
- **Code Snippet:**
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```

### Recommended Changes
In `viking_girlfriend_skill/data/knowledge_reference/populate.py`, `urllib.request.urlopen` is used to fetch data from Wikipedia's API. While the base URLs (`https://en.wikipedia.org/...`) are hardcoded, it is best practice (and often required to pass strict security gates) to explicitly validate that the URL scheme is secure (i.e., `http` or `https`) before opening it. Once the scheme is validated, the Bandit finding can be suppressed with `# nosec B310`.

**Suggested Code Update in `viking_girlfriend_skill/data/knowledge_reference/populate.py` (for both occurrences):**

Add a validation check before the `urlopen` call:
```python
            try:
                if not url.startswith(('http://', 'https://')):
                    raise ValueError("Invalid URL scheme")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
                    data = json.loads(response.read().decode())
```
