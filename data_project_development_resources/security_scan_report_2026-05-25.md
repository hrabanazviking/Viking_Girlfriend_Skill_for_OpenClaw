# Security Scan and Bug Report
Date: 2026-05-25

## Findings

### 1. Possible execution of untrusted input (B404/B603)
**File:** `infra/bootstrap_host.py`
**Lines:** 3, 15
**Details:** Bandit warns about `import subprocess` (B404) and `subprocess.run` (B603) because they can execute arbitrary commands. The documentation for B603 notes it looks for spawning of a subprocess without the use of a command shell, warning that appropriate care must be taken to sanitize user-provided or variable input. However, the input to `subprocess.run` is hardcoded (e.g., `"podman"`, `"docker"`).
**Recommended Code Changes:**
Append `# nosec B404` to `import subprocess` and `# nosec B603` to the `subprocess.run` line.

```python
import subprocess  # nosec B404

# ...
subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
```

### 2. Try, Except, Pass (B110)
**File:** `tests/test_cove_pipeline.py` (line 256), `tests/test_e2e_system.py` (line 169)
**Details:** Generic exceptions are caught and ignored with `pass`. Bandit documentation flags this as it can hide important application errors.
**Recommended Code Changes:**
Append `# nosec B110` to the `pass` lines, as they are intentional in these tests.

```python
        except Exception:
            pass  # nosec B110
```

### 3. Unsafe `urlopen` scheme (B310)
**File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Lines:** 27, 62
**Details:** Using `urllib.request.urlopen` without validating the scheme can lead to SSRF or Path Traversal if untrusted input is passed as a URL. Bandit documentation warns: "Audit url open for permitted schemes. Allowing use of 'file:' or custom schemes is often unexpected."
**Recommended Code Changes:**
Validate that the URL scheme is HTTP/HTTPS before calling `urlopen`, and then append `# nosec B310` to the `urlopen` line.

```python
            if not url.startswith(('http://', 'https://')):
                raise ValueError("Invalid URL scheme")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
```

## Research Resources
- **Bandit Documentation (B404):** Blacklists Python modules known to have possible security implications (https://bandit.readthedocs.io/_/downloads/en/1.7.5/pdf/).
- **Bandit Documentation (B603):** Warns about subprocess invocations without shell=True which might be unsafe if variables are not sanitized (https://bandit.readthedocs.io/en/latest/plugins/b603_subprocess_without_shell_equals_true.html).
- **Bandit Documentation (B110):** Warns about catching and silently ignoring generic exceptions (try_except_pass).
- **Bandit Documentation (B310):** Flags urllib_urlopen usage and advises auditing for permitted schemes like http/https (https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html).
