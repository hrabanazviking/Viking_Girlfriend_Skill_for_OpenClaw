# Security Scan Report

**Date:** 2026-05-24

## Overview
A security scan was performed using Bandit (Static Application Security Testing tool for Python). The scan identified several potential security issues. Note that `assert_used` (B101) warnings were ignored as they are mostly present in test files.

## Identified Issues

### Issue 1: B404 - blacklist
- **File:** `./infra/bootstrap_host.py`
- **Line Number:** 3
- **Severity:** LOW
- **Confidence:** HIGH
- **CWE:** [78](https://cwe.mitre.org/data/definitions/78.html)
- **Description:** Consider possible security implications associated with the subprocess module.
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess
#### Code Snippet:
```python
2 import sys
3 import subprocess
4 import platform
```

#### Recommended Code Change & Research:
The `subprocess` module can be dangerous if used with untrusted input (e.g., shell injection). However, in `infra/bootstrap_host.py`, the command executed is `subprocess.run([command, "--version"], capture_output=True, check=True)`. Since `shell=False` is used (default) and it's executing a static command array without user input passed to a shell, this is generally safe. To suppress these Bandit warnings, append `# nosec B404` to the import and `# nosec B603` to the `subprocess.run` call.

### Issue 2: B603 - subprocess_without_shell_equals_true
- **File:** `./infra/bootstrap_host.py`
- **Line Number:** 15
- **Severity:** LOW
- **Confidence:** HIGH
- **CWE:** [78](https://cwe.mitre.org/data/definitions/78.html)
- **Description:** subprocess call - check for execution of untrusted input.
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html
#### Code Snippet:
```python
14     try:
15         subprocess.run([command, "--version"], capture_output=True, check=True)
16         return True
```

#### Recommended Code Change & Research:
The `subprocess` module can be dangerous if used with untrusted input (e.g., shell injection). However, in `infra/bootstrap_host.py`, the command executed is `subprocess.run([command, "--version"], capture_output=True, check=True)`. Since `shell=False` is used (default) and it's executing a static command array without user input passed to a shell, this is generally safe. To suppress these Bandit warnings, append `# nosec B404` to the import and `# nosec B603` to the `subprocess.run` call.

### Issue 3: B110 - try_except_pass
- **File:** `./tests/test_cove_pipeline.py`
- **Line Number:** 256
- **Severity:** LOW
- **Confidence:** HIGH
- **CWE:** [703](https://cwe.mitre.org/data/definitions/703.html)
- **Description:** Try, Except, Pass detected.
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html
#### Code Snippet:
```python
255             cove._cb_pipeline.on_failure(RuntimeError("test failure"))
256         except Exception:
257             pass
258
```

#### Recommended Code Change & Research:
The `try-except-pass` pattern is discouraged because it silently ignores errors. In `tests/test_cove_pipeline.py` and `tests/test_e2e_system.py`, catching generic `Exception` and passing can mask critical test failures or unexpected system states. It is recommended to log the exception using a logger or at least print the warning rather than silently passing, or configure Bandit to ignore typed exceptions if passing is intended for a specific error type.

### Issue 4: B110 - try_except_pass
- **File:** `./tests/test_e2e_system.py`
- **Line Number:** 169
- **Severity:** LOW
- **Confidence:** HIGH
- **CWE:** [703](https://cwe.mitre.org/data/definitions/703.html)
- **Description:** Try, Except, Pass detected.
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html
#### Code Snippet:
```python
168             asyncio.run(bus.publish_state(ev, nowait=True))
169         except Exception:
170             pass  # offline / loop not running — acceptable
171
```

#### Recommended Code Change & Research:
The `try-except-pass` pattern is discouraged because it silently ignores errors. In `tests/test_cove_pipeline.py` and `tests/test_e2e_system.py`, catching generic `Exception` and passing can mask critical test failures or unexpected system states. It is recommended to log the exception using a logger or at least print the warning rather than silently passing, or configure Bandit to ignore typed exceptions if passing is intended for a specific error type.

### Issue 5: B310 - blacklist
- **File:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line Number:** 27
- **Severity:** MEDIUM
- **Confidence:** HIGH
- **CWE:** [22](https://cwe.mitre.org/data/definitions/22.html)
- **Description:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen
#### Code Snippet:
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```

#### Recommended Code Change & Research:
The `urllib.request.urlopen` function allows reading from any scheme, including `file://`, which could lead to Local File Inclusion or Server-Side Request Forgery (SSRF) if the URL is user-controlled. In `viking_girlfriend_skill/data/knowledge_reference/populate.py`, the URL should be validated to ensure it starts with `http://` or `https://` before opening. After validation, append `# nosec B310` to the `urlopen` line to suppress the warning.
Example fix:
```python
if not url.startswith('http://') and not url.startswith('https://'):
    raise ValueError('Invalid URL scheme')
with urllib.request.urlopen(req) as response:  # nosec B310
```

### Issue 6: B310 - blacklist
- **File:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line Number:** 62
- **Severity:** MEDIUM
- **Confidence:** HIGH
- **CWE:** [22](https://cwe.mitre.org/data/definitions/22.html)
- **Description:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen
#### Code Snippet:
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```

#### Recommended Code Change & Research:
The `urllib.request.urlopen` function allows reading from any scheme, including `file://`, which could lead to Local File Inclusion or Server-Side Request Forgery (SSRF) if the URL is user-controlled. In `viking_girlfriend_skill/data/knowledge_reference/populate.py`, the URL should be validated to ensure it starts with `http://` or `https://` before opening. After validation, append `# nosec B310` to the `urlopen` line to suppress the warning.
Example fix:
```python
if not url.startswith('http://') and not url.startswith('https://'):
    raise ValueError('Invalid URL scheme')
with urllib.request.urlopen(req) as response:  # nosec B310
```


---
*End of Report*
