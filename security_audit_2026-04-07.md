# Security Audit Report - 2026-04-07

## Overview
A comprehensive static application security testing (SAST) scan was performed using Bandit across the entire codebase. The scan identified a few low-severity issues related to `subprocess` execution and a medium-severity issue related to Server-Side Request Forgery (SSRF) vulnerabilities when fetching online data via `urllib.request.urlopen`.

## Findings

### 1. SSRF / Local File Inclusion Vulnerability (Medium Severity)
**Issue ID:** BAN-B310 (Bandit B310)
**CWE:** CWE-22
**Location:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Lines 27, 62)
**Description:**
The script `populate.py` uses `urllib.request.urlopen` to fetch data from Wikipedia based on categories. The `urlopen` function supports `file://`, `ftp://`, and custom schemes in addition to `http://` and `https://`. Opening untrusted URLs could lead to Server-Side Request Forgery (SSRF) or expose local files (Local File Inclusion) if the URL is maliciously crafted or redirects unexpectedly. Even though the URLs currently seem hardcoded to `en.wikipedia.org`, it's a best practice to validate the scheme before opening the connection.

**Recommended Code Changes:**
Validate the URL scheme to ensure it only allows `http` or `https` before making the request.

```python
<<<<<<< SEARCH
        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
=======
        while True:
            try:
                if not url.lower().startswith(('http://', 'https://')):
                    raise ValueError(f"Invalid URL scheme: {url}")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                # nosec B310 - URL scheme validated above
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

```python
<<<<<<< SEARCH
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                pages = data['query']['pages']
=======
        try:
            if not url.lower().startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL scheme: {url}")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            # nosec B310 - URL scheme validated above
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                pages = data['query']['pages']
>>>>>>> REPLACE
```

### 2. Insecure Use of Subprocess (Low Severity)
**Issue ID:** BAN-B404 & BAN-B603 (Bandit B404, B603)
**CWE:** CWE-78
**Location:** `infra/bootstrap_host.py` (Line 15)
**Description:**
The `check_command` function uses `subprocess.run([command, "--version"], ...)` where `command` is passed as a string argument. While `shell=True` is not used (which is good), executing a command based on an unsanitized variable might still pose a risk if the input string originates from an untrusted source. In this context, it seems `command` comes from hardcoded values (`"podman"`, `"docker"`, `"nvidia-smi"`), so the risk is minimal.

**Recommended Code Changes:**
Ensure that `command` is always sanitized and checked against a whitelist of allowed executables before being passed to `subprocess.run`.

```python
<<<<<<< SEARCH
def check_command(command: str) -> bool:
    """Check if a command is available on the host system."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
=======
def check_command(command: str) -> bool:
    """Check if a command is available on the host system."""
    allowed_commands = {"podman", "docker", "nvidia-smi"}
    if command not in allowed_commands:
        logger.error(f"Command '{command}' is not in the allowed list.")
        return False
    try:
        # nosec B603 - Command is validated against an allowlist
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False
>>>>>>> REPLACE
```

### 3. Use of `assert` in tests
**Issue ID:** BAN-B101 (Bandit B101)
**CWE:** CWE-703
**Description:**
Bandit warns about the use of `assert` statements. This is because `assert` is removed when Python compiles to optimized byte code (using the `-O` flag), which can lead to bugs if assertions are used for flow control or side effects. However, in this project, `assert` is used exclusively within `pytest` test files, which is the standard and correct way to write tests in pytest. No changes are required.
