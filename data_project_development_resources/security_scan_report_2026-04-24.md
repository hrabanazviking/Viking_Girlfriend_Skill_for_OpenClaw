# Security Code Scan Report (2026-04-24)

## Overview
Found 6 security issues in the codebase.

## Detailed Findings

### 1. B404: blacklist (LOW Severity)
- **File:** `./infra/bootstrap_host.py`
- **Line:** 3
- **Description:** Consider possible security implications associated with the subprocess module.
- **CWE:** [78](https://cwe.mitre.org/data/definitions/78.html)

**Code snippet:**
```python
2 import sys
3 import subprocess
4 import platform
```

[Bandit Documentation for B404](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_imports.html#b404-import-subprocess)

---

### 2. B603: subprocess_without_shell_equals_true (LOW Severity)
- **File:** `./infra/bootstrap_host.py`
- **Line:** 15
- **Description:** subprocess call - check for execution of untrusted input.
- **CWE:** [78](https://cwe.mitre.org/data/definitions/78.html)

**Code snippet:**
```python
14     try:
15         subprocess.run([command, "--version"], capture_output=True, check=True)
16         return True
```


#### Research Data for B603 & B404: Subprocess Execution
> **Analysis:** The `subprocess` module is a common source of security vulnerabilities (command injection) if user input is passed unsafely. However, the `infra/bootstrap_host.py` script appears to be using hardcoded strings (`[command, "--version"]`) in the `subprocess.run` call, which is inherently safe from command injection.
>
> **Recommendation:** Since the command being executed does not rely on untrusted input, these are false positives. You should suppress them by appending `# nosec B404` and `# nosec B603` to the import statement and `subprocess.run` call respectively.
>
> Example Fix in `infra/bootstrap_host.py`:
> ```python
> import sys
> import subprocess # nosec B404
> import platform
> ...
>     try:
>         subprocess.run([command, "--version"], capture_output=True, check=True) # nosec B603
>         return True
> ```

[Bandit Documentation for B603](https://bandit.readthedocs.io/en/1.9.4/plugins/b603_subprocess_without_shell_equals_true.html)

---

### 3. B110: try_except_pass (LOW Severity)
- **File:** `./tests/test_cove_pipeline.py`
- **Line:** 256
- **Description:** Try, Except, Pass detected.
- **CWE:** [703](https://cwe.mitre.org/data/definitions/703.html)

**Code snippet:**
```python
255             cove._cb_pipeline.on_failure(RuntimeError("test failure"))
256         except Exception:
257             pass
258
```


#### Research Data for B110: try_except_pass
> **Analysis:** Silently ignoring exceptions (`except Exception: pass`) is bad practice as it can hide critical errors and lead to corrupted state. While this might be acceptable in test code (like `tests/test_cove_pipeline.py` and `tests/test_e2e_system.py`), it's generally better to log the exception or handle it explicitly.
>
> **Recommendation:** Replace `pass` with a logging statement, or if it is intentionally ignored, document it clearly or use `contextlib.suppress`. For test code, you could consider leaving it or adding `# nosec B110` to suppress the warning explicitly if you know it's safe.
>
> Example Fix:
> ```python
>         except Exception as e:
>             logger.warning(f"Failed to publish state: {e}")
> ```

[Bandit Documentation for B110](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

---

### 4. B110: try_except_pass (LOW Severity)
- **File:** `./tests/test_e2e_system.py`
- **Line:** 169
- **Description:** Try, Except, Pass detected.
- **CWE:** [703](https://cwe.mitre.org/data/definitions/703.html)

**Code snippet:**
```python
168             asyncio.run(bus.publish_state(ev, nowait=True))
169         except Exception:
170             pass  # offline / loop not running — acceptable
171
```


#### Research Data for B110: try_except_pass
> **Analysis:** Silently ignoring exceptions (`except Exception: pass`) is bad practice as it can hide critical errors and lead to corrupted state. While this might be acceptable in test code (like `tests/test_cove_pipeline.py` and `tests/test_e2e_system.py`), it's generally better to log the exception or handle it explicitly.
>
> **Recommendation:** Replace `pass` with a logging statement, or if it is intentionally ignored, document it clearly or use `contextlib.suppress`. For test code, you could consider leaving it or adding `# nosec B110` to suppress the warning explicitly if you know it's safe.
>
> Example Fix:
> ```python
>         except Exception as e:
>             logger.warning(f"Failed to publish state: {e}")
> ```

[Bandit Documentation for B110](https://bandit.readthedocs.io/en/1.9.4/plugins/b110_try_except_pass.html)

---

### 5. B310: blacklist (MEDIUM Severity)
- **File:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line:** 27
- **Description:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **CWE:** [22](https://cwe.mitre.org/data/definitions/22.html)

**Code snippet:**
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```

#### Research Data for B310: urllib_urlopen
> **Analysis:** The use of `urllib.request.urlopen` can lead to Server-Side Request Forgery (SSRF) or Local File Inclusion (LFI) if the URL is not properly validated. The `file://` scheme or custom schemes might be allowed, which is dangerous when processing untrusted inputs.
>
> **Recommendation:** Explicitly validate that the URL scheme is either `http://` or `https://` before opening the URL. After validation, you can append `# nosec B310` to suppress the Bandit warning.
>
> Example Fix:
> ```python
> from urllib.parse import urlparse
>
> parsed = urlparse(url)
> if parsed.scheme not in ('http', 'https'):
>     raise ValueError("Invalid URL scheme")
>
> req = urllib.request.Request(url, headers={'User-Agent': '...'})
> with urllib.request.urlopen(req) as response:  # nosec B310
>     ...
> ```

[Bandit Documentation for B310](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen)

---

### 6. B310: blacklist (MEDIUM Severity)
- **File:** `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line:** 62
- **Description:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **CWE:** [22](https://cwe.mitre.org/data/definitions/22.html)

**Code snippet:**
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```

#### Research Data for B310: urllib_urlopen
> **Analysis:** The use of `urllib.request.urlopen` can lead to Server-Side Request Forgery (SSRF) or Local File Inclusion (LFI) if the URL is not properly validated. The `file://` scheme or custom schemes might be allowed, which is dangerous when processing untrusted inputs.
>
> **Recommendation:** Explicitly validate that the URL scheme is either `http://` or `https://` before opening the URL. After validation, you can append `# nosec B310` to suppress the Bandit warning.
>
> Example Fix:
> ```python
> from urllib.parse import urlparse
>
> parsed = urlparse(url)
> if parsed.scheme not in ('http', 'https'):
>     raise ValueError("Invalid URL scheme")
>
> req = urllib.request.Request(url, headers={'User-Agent': '...'})
> with urllib.request.urlopen(req) as response:  # nosec B310
>     ...
> ```

[Bandit Documentation for B310](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen)

---
