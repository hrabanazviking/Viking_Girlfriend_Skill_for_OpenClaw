# Security Scan Report - 2026-05-08

## Overview
A static application security testing (SAST) scan was performed across the codebase using `bandit`. Several security issues were identified and reviewed.

## Findings

### 1. `subprocess` Module Usage (B404, B603)
**Files:** `infra/bootstrap_host.py`
**Severity:** Low
**Confidence:** High

**Description:**
Bandit flagged the import of the `subprocess` module (B404) and the usage of `subprocess.run` (B603) without `shell=True`.
While `shell=False` is safer than `shell=True`, Bandit still flags this to prompt a manual review ensuring that the input passed to the subprocess call is trusted. In this specific case, the `command` variable is passed directly as part of an array (`[command, "--version"]`). Since the commands being checked are hardcoded in the script (`podman`, `docker`, `nvidia-smi`), this is not a true vulnerability.

**Recommended Code Change:**
Suppress the warnings using `# nosec` as per the project's memory directives, since the commands are static and trusted.

```python
import subprocess  # nosec B404

def check_command(command: str) -> bool:
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
```

### 2. Unvalidated URL schemes in `urllib.request.urlopen` (B310)
**Files:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (lines 27, 62)
**Severity:** Medium
**Confidence:** High

**Description:**
Bandit flagged the use of `urllib.request.urlopen` because it can open various URL schemes, including `file://`, potentially leading to Server-Side Request Forgery (SSRF) or Local File Inclusion (LFI) / Path Traversal vulnerabilities if the URL contains unsanitized input.
Although the base URLs in this script are currently hardcoded to `https://en.wikipedia.org/...`, best practices dictate that the URL scheme should be explicitly validated before opening it to ensure it is limited to `http` or `https`.

**Recommended Code Change:**
Add a validation check for the URL scheme to ensure it starts with `http://` or `https://` before opening, and then apply `# nosec B310`.

```python
# Validation check before line 27
if not url.lower().startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    data = json.loads(response.read().decode())
```

```python
# Validation check before line 62
if not url.lower().startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    data = json.loads(response.read().decode())
```

## Research Resources
- **Bandit B404:** [https://bandit.readthedocs.io/en/latest/blacklists/blacklist_imports.html#b404-import-subprocess](https://bandit.readthedocs.io/en/latest/blacklists/blacklist_imports.html#b404-import-subprocess)
- **Bandit B603:** [https://bandit.readthedocs.io/en/latest/plugins/b603_subprocess_without_shell_equals_true.html](https://bandit.readthedocs.io/en/latest/plugins/b603_subprocess_without_shell_equals_true.html)
- **Bandit B310:** [https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b310-urllib-urlopen](https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b310-urllib-urlopen)
- **SSRF via `urllib`:** [Stack Overflow: Audit url open for permitted schemes.](https://stackoverflow.com/questions/48779202/audit-url-open-for-permitted-schemes-allowing-use-of-file-or-custom-schemes)
