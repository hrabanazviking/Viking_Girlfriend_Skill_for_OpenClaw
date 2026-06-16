# Security Scan Report

## Overview
A static application security testing (SAST) scan was performed on the codebase using `bandit` on 2026-04-27. The scan identified the following security warnings that require review and potential mitigation.

---

## 1. Subprocess Execution Issues
### Files Affected
* `infra/bootstrap_host.py`
    * Line 3: `import subprocess` (Bandit B404: blacklist)
    * Line 15: `subprocess.run([command, "--version"], capture_output=True, check=True)` (Bandit B603: subprocess_without_shell_equals_true)

### Issue Description
The `subprocess` module provides a way to spawn new processes, which can pose a security risk (Command Injection) if untrusted data is passed to commands without validation.
* **B404 (blacklist):** Bandit flags the import of `subprocess` globally as a low-severity issue, alerting developers to the potential security implications.
* **B603 (subprocess_without_shell_equals_true):** Bandit flags calls to `subprocess.run`, `Popen`, etc., even with `shell=False`, as untrusted input passed to arguments could still result in unintended execution behavior depending on the executable being called.

### Research Data
According to the Bandit documentation and security reports on HackerOne, passing untrusted variables directly into subprocess calls (such as `args`) allows an attacker to inject arbitrary commands if inputs are not sanitized. Since `shell=False` is used (by default), shell injection is mitigated, but argument injection could still occur if `command` is controlled by a user.

### Recommended Code Changes
In `infra/bootstrap_host.py`, the `command` argument passed to `subprocess.run` comes directly from the internal script logic (`"podman"`, `"docker"`, `"nvidia-smi"`), so it is not user-controlled. Therefore, this is a false positive in the context of user input. To resolve the warnings, `nosec` comments should be added:
```python
import subprocess  # nosec B404

# ... inside check_command() ...
subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
```

---

## 2. Unrestricted URL Schemes
### Files Affected
* `viking_girlfriend_skill/data/knowledge_reference/populate.py`
    * Line 27: `with urllib.request.urlopen(req) as response:` (Bandit B310: blacklist)
    * Line 62: `with urllib.request.urlopen(req) as response:` (Bandit B310: blacklist)

### Issue Description
The `urllib.request.urlopen` function is flagged (Bandit B310) because it can open not only `http://` or `https://` URLs, but also `ftp://` and `file://` schemes. If the URL being opened is manipulated by an external user, it might be possible to access local files on the executing machine (e.g., via `file:///etc/passwd`), leading to Server-Side Request Forgery (SSRF) or Path Traversal vulnerabilities.

### Research Data
Bandit specifically audits `urlopen` for permitted schemes. Allowing the use of `file:/` or custom schemes is often unexpected and a major security vulnerability. While the current script logic hardcodes the base URL as `https://en.wikipedia.org/w/api.php`, best practices dictate explicitly verifying the URL scheme before calling `urlopen`, or suppressing the warning if the URL is strictly internally controlled.

### Recommended Code Changes
To fix this issue and suppress the linter warnings, validate the URL scheme to ensure it starts with `http` or `https`. Once validated, append `# nosec B310` to the `urlopen` line:

```python
# Apply this pattern to lines 27 and 62:
if not url.lower().startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    data = json.loads(response.read().decode())
```
