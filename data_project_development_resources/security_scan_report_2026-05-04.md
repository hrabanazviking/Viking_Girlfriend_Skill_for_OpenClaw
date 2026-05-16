# Security Audit Report (2026-05-04)

This report lists the security issues found during the audit, along with recommended fixes and research on the issues.

## B404 - LOW Severity
**File:** ./infra/bootstrap_host.py:3

**Description:** Consider possible security implications associated with the subprocess module.

**More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess

**Code snippet:**
```python
2 import sys
3 import subprocess
4 import platform

```

**Research & Recommendations:**
The `subprocess` module can be used to execute external commands. If untrusted input is passed to `subprocess` functions without proper sanitization, it can lead to command injection vulnerabilities. To fix this warning, if the use of `subprocess` is safe and does not involve untrusted input, append `# nosec B404` to the import statement to suppress the warning.

## B603 - LOW Severity
**File:** ./infra/bootstrap_host.py:15

**Description:** subprocess call - check for execution of untrusted input.

**More Info:** https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html

**Code snippet:**
```python
14     try:
15         subprocess.run([command, "--version"], capture_output=True, check=True)
16         return True

```

**Research & Recommendations:**
Using `subprocess` without `shell=True` is generally safer as it avoids shell injection attacks. However, it is still important to ensure that the input is trusted or sanitized. If the command executed is static or hardcoded and does not include any user-provided input, it is safe. To fix this warning, append `# nosec B603` to the function call line to suppress the warning.

## B110 - LOW Severity
**File:** ./tests/test_cove_pipeline.py:256

**Description:** Try, Except, Pass detected.

**More Info:** https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html

**Code snippet:**
```python
255             cove._cb_pipeline.on_failure(RuntimeError("test failure"))
256         except Exception:
257             pass
258

```

**Research & Recommendations:**
A `try-except-pass` block catches an exception but does nothing to handle it, which can silently ignore errors and make debugging difficult. It might also mask security issues if important exceptions are ignored. If silencing the exception is intentional and safe, it's better to explicitly catch specific exceptions rather than a generic `Exception`. To suppress this warning if you are sure it is safe, append `# nosec B110`.

## B110 - LOW Severity
**File:** ./tests/test_e2e_system.py:169

**Description:** Try, Except, Pass detected.

**More Info:** https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html

**Code snippet:**
```python
168             asyncio.run(bus.publish_state(ev, nowait=True))
169         except Exception:
170             pass  # offline / loop not running — acceptable
171

```

**Research & Recommendations:**
A `try-except-pass` block catches an exception but does nothing to handle it, which can silently ignore errors and make debugging difficult. It might also mask security issues if important exceptions are ignored. If silencing the exception is intentional and safe, it's better to explicitly catch specific exceptions rather than a generic `Exception`. To suppress this warning if you are sure it is safe, append `# nosec B110`.

## B310 - MEDIUM Severity
**File:** ./viking_girlfriend_skill/data/knowledge_reference/populate.py:27

**Description:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

**More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

**Code snippet:**
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())

```

**Research & Recommendations:**
The `urllib.request.urlopen` function can open various types of URLs, including `file://` schemes. If untrusted input is used to construct the URL, an attacker could read arbitrary local files (Path Traversal) or make requests to internal services (SSRF). To mitigate this, explicitly validate the URL scheme to ensure it starts with `http://` or `https://` before passing it to `urlopen`. For example:
```python
if not url.startswith('http://') and not url.startswith('https://'):
    raise ValueError('Invalid URL scheme')
```
After adding the validation, append `# nosec B310` to the `urlopen` call to suppress the warning.

## B310 - MEDIUM Severity
**File:** ./viking_girlfriend_skill/data/knowledge_reference/populate.py:62

**Description:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

**More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen

**Code snippet:**
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())

```

**Research & Recommendations:**
The `urllib.request.urlopen` function can open various types of URLs, including `file://` schemes. If untrusted input is used to construct the URL, an attacker could read arbitrary local files (Path Traversal) or make requests to internal services (SSRF). To mitigate this, explicitly validate the URL scheme to ensure it starts with `http://` or `https://` before passing it to `urlopen`. For example:
```python
if not url.startswith('http://') and not url.startswith('https://'):
    raise ValueError('Invalid URL scheme')
```
After adding the validation, append `# nosec B310` to the `urlopen` call to suppress the warning.
