# Security Scan Report: 2026-05-27

A static application security testing (SAST) scan was performed using Bandit on the OpenClaw Viking Companion Skill codebase.

The scan ignored `B101: assert_used` warnings, as they are expected in the project's test suite, but identified other warnings that require attention.

## Identified Vulnerabilities and Research Data

### 1. B404: import_subprocess & B603: subprocess_without_shell_equals_true
**Affected File:** `infra/bootstrap_host.py`
- Line 3: `import subprocess` (B404)
- Line 15: `subprocess.run([command, "--version"], capture_output=True, check=True)` (B603)

**Description & Research:**
- **B404:** Bandit flags the import of the `subprocess` module as a reminder to check for potential security implications when spawning child processes.
- **B603:** Bandit warns when `subprocess` is used without `shell=True`. While safer than `shell=True`, it is still essential to ensure the input passed to the command (in this case, `command`) is safe and not influenced by untrusted user input to prevent command injection.
- **Reference:** https://bandit.readthedocs.io/en/latest/plugins/b603_subprocess_without_shell_equals_true.html

**Recommended Code Change:**
Since `check_command(command: str)` in `infra/bootstrap_host.py` receives hardcoded values like `"podman"` and `"docker"` within the same file, the risk is minimal. However, to silence the Bandit warnings, you should append `# nosec B404` and `# nosec B603` to the respective lines.

```python
import sys
import subprocess  # nosec B404
import platform
# ...
def check_command(command: str) -> bool:
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
        return True
# ...
```

---

### 2. B110: try_except_pass
**Affected Files:**
- `tests/test_cove_pipeline.py` (Line 256)
- `tests/test_e2e_system.py` (Line 169)

**Description & Research:**
- **B110:** This plugin detects the use of `pass` within an `except Exception:` block. Catching base `Exception` and silently ignoring it is considered bad practice because it can hide actual bugs or mask disruption attempts. It is generally recommended to at least log the error or catch specific exception types rather than the base class.
- **Reference:** https://bandit.readthedocs.io/en/latest/plugins/b110_try_except_pass.html

**Recommended Code Change:**
In test environments, sometimes `try...except...pass` is used intentionally (e.g., simulating a failure or ignoring a closed event loop). To resolve the Bandit warning, you can append `# nosec B110` to the lines if the suppression is deliberate.

For `tests/test_cove_pipeline.py`:
```python
        except Exception:  # nosec B110
            pass
```

For `tests/test_e2e_system.py`:
```python
        except Exception:  # nosec B110
            pass  # offline / loop not running — acceptable
```

---

### 3. B310: urllib_urlopen
**Affected File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- Line 27: `with urllib.request.urlopen(req) as response:`
- Line 62: `with urllib.request.urlopen(req) as response:`

**Description & Research:**
- **B310:** Bandit flags the use of `urllib.request.urlopen` because it can open any URL scheme. If untrusted input influences the URL, this can lead to Server-Side Request Forgery (SSRF) or arbitrary local file reads via the `file://` scheme or other custom schemes.
- **Reference:** https://static.openstack.org/docs/bandit/latest/api/bandit.blacklists.html

**Recommended Code Change:**
Before passing the `url` variable to `urllib.request.urlopen`, explicitly validate the scheme to ensure it strictly permits `http://` or `https://` schemes. After validation, you can append `# nosec B310` to suppress the Bandit warning.

```python
                    # Inside fetch_category_members
                    if not url.startswith(('http://', 'https://')):
                        raise ValueError("Invalid URL scheme")
                    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                    with urllib.request.urlopen(req) as response:  # nosec B310
```

```python
            # Inside fetch_extracts_in_batches
            if not url.startswith(('http://', 'https://')):
                 raise ValueError("Invalid URL scheme")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
```
