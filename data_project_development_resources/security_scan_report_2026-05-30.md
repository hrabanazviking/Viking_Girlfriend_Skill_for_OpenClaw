# Security Scan Report

## Overview
A security scan was conducted using Bandit. Several issues were identified, and recommended fixes are documented below.

## Findings

### 1. Insecure Use of `urllib.request.urlopen` (B310)
**Location:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Lines 27, 62)
**Severity:** MEDIUM
**CWE:** [CWE-22](https://cwe.mitre.org/data/definitions/22.html) - Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal') / Server-Side Request Forgery (SSRF)

**Description:**
Bandit reported `Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.`
Using `urllib.request.urlopen` without validating the scheme can lead to Server-Side Request Forgery (SSRF) or Local File Inclusion (LFI) if an attacker can control the URL (e.g., using a `file://` scheme instead of `https://`).

**Recommendation:**
Validate the URL scheme before calling `urlopen`. Make sure it starts with `http://` or `https://`. After validating, you can append `# nosec B310` to suppress the Bandit warning.

**Proposed Code Change in `viking_girlfriend_skill/data/knowledge_reference/populate.py`:**
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
                    raise ValueError("Invalid URL scheme")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
                    data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

```python
<<<<<<< SEARCH
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
=======
        try:
            if not url.lower().startswith(('http://', 'https://')):
                raise ValueError("Invalid URL scheme")
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
                data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

### 2. Subprocess calls with untrusted input (B404, B603)
**Location:** `infra/bootstrap_host.py` (Line 3, Line 15)
**Severity:** LOW
**CWE:** [CWE-78](https://cwe.mitre.org/data/definitions/78.html) - Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')

**Description:**
Bandit reported `B404: import_subprocess` and `B603: subprocess_without_shell_equals_true`.
The `subprocess.run` call might execute untrusted input if the `command` variable can be manipulated by an attacker. Although this is less risky since `shell=False` is used implicitly, it's still good practice to suppress the warnings if the input is considered safe or hardcoded. The inputs in `verify_host` are hardcoded ("podman", "docker", "nvidia-smi").

**Recommendation:**
Since the command inputs in `bootstrap_host.py` are static ("podman", "docker", "nvidia-smi"), it is safe to suppress these warnings.

**Proposed Code Change in `infra/bootstrap_host.py`:**
```python
<<<<<<< SEARCH
import sys
import subprocess
import platform
=======
import sys
import subprocess  # nosec B404
import platform
>>>>>>> REPLACE
```

```python
<<<<<<< SEARCH
def check_command(command: str) -> bool:
    """Check if a command is available on the host system."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
=======
def check_command(command: str) -> bool:
    """Check if a command is available on the host system."""
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
        return True
>>>>>>> REPLACE
```

## Ignored Warnings
Many B101 (Use of assert) warnings were detected. As these are exclusively within the `tests/` directory and are the standard way `pytest` evaluates test conditions, they are deemed false positives and are safely ignored.
B110 (try-except-pass) in tests are also common for ignoring expected exceptions during teardown or mocked failure scenarios, and are ignored here.
