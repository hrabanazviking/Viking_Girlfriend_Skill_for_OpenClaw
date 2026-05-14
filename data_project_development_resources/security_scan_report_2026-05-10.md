# Security Scan Report

**Date:** 2026-05-10

## Overview

A static application security testing (SAST) scan was performed using Bandit on the Viking Girlfriend Skill codebase. The scan identified several potential security issues. This report details the findings, provides research context based on CWE classifications, and outlines recommended code changes.

## Findings

### 1. Subprocess Module Vulnerabilities (Bandit B404/B603)

*   **File:** `infra/bootstrap_host.py`
*   **Lines:** 3 (B404), 15 (B603)
*   **Severity:** Low (Context-dependent)
*   **CWE Reference:** CWE-78: Improper Neutralization of Special Elements used in an OS Command ('OS Command Injection')

**Description:**
Bandit flagged the importation of the `subprocess` module (B404) and its usage (B603). The `subprocess` module is inherently powerful as it allows a Python script to spawn new processes, connect to their input/output/error pipes, and obtain their return codes.

**Research Context (CWE-78):**
As detailed by CWE-78, OS Command Injection occurs when an application constructs an OS command using externally influenced input without proper neutralization. If an attacker can control the arguments passed to `subprocess.Popen` or `subprocess.run`, they might be able to inject arbitrary shell commands.

*Mitigation:* The primary mitigation is to avoid `shell=True` (which is already the case here) and to ensure that all arguments passed to `subprocess` functions are either hardcoded or strictly validated against an allowlist.

**Analysis of `infra/bootstrap_host.py`:**
The `check_command` function uses `subprocess.run([command, "--version"], capture_output=True, check=True)`. The `command` argument is passed internally by `verify_host` and consists of hardcoded strings like `"podman"`, `"docker"`, and `"nvidia-smi"`. Because the input is not user-controlled and `shell=True` is not used, this specific usage is safe from command injection.

**Recommended Code Changes:**
To resolve the Bandit warnings while acknowledging the safety of the current implementation, we should append `# nosec` tags to the specific lines. This suppresses the false positives.

```python
<<<<<<< SEARCH
import subprocess
=======
import subprocess  # nosec B404
>>>>>>> REPLACE
```

```python
<<<<<<< SEARCH
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)
        return True
=======
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
        return True
>>>>>>> REPLACE
```

### 2. Urllib Scheme Vulnerabilities (Bandit B310)

*   **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
*   **Lines:** 27, 62
*   **Severity:** Medium
*   **CWE Reference:** CWE-918: Server-Side Request Forgery (SSRF)

**Description:**
Bandit flagged the use of `urllib.request.urlopen`. `urllib` can open not only `http://` or `https://` URLs, but also `ftp://` and `file://` URLs. If the URL passed to `urlopen` is influenced by an external user, it could allow an attacker to read local files on the server (e.g., `file:///etc/passwd`) or interact with internal network services.

**Research Context (CWE-918 / DeepSource BAN-B310):**
Server-Side Request Forgery (SSRF) occurs when a web server receives a URL from an upstream component and retrieves its contents without ensuring the destination is expected or safe. Attackers can use the server as a proxy to access internal network resources or local files. DeepSource specifically warns about this in relation to `urllib` (BAN-B310), recommending explicit validation of the URL scheme before opening it.

*Mitigation:* Validate the user-provided URL to ensure it begins with an expected scheme (like `http://` or `https://`).

**Analysis of `viking_girlfriend_skill/data/knowledge_reference/populate.py`:**
The `populate.py` script constructs URLs dynamically based on Wikipedia categories. While the base URL (`https://en.wikipedia.org/w/api.php...`) is hardcoded, it's best practice to validate the URL scheme before calling `urlopen` to ensure no unexpected manipulation has occurred during URL construction or parameter encoding.

**Recommended Code Changes:**
Add explicit URL validation to ensure the scheme is `http` or `https` before opening the URL, and then suppress the Bandit warning.

For line 27:
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

For line 62:
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
