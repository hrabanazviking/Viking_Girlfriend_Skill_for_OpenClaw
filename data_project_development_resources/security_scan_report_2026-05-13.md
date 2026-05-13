# Security Scan Report: 2026-05-13

## Identified Issues

### Server-Side Request Forgery (SSRF) / Path Traversal (CWE-22)
**Severity:** MEDIUM
**Confidence:** HIGH

Bandit scan detected two instances of `urllib.request.urlopen(req)` without explicit URL scheme validation, which can allow use of the `file://` scheme or custom schemes, potentially leading to path traversal or unintended file access on the host system.

**Files & Lines:**
* `./viking_girlfriend_skill/data/knowledge_reference/populate.py` (Line 27, 62)

**Code Context:**
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```

### Research
According to CWE-22 (Path Traversal), allowing user-supplied input to dictate parts of a filepath (or a `file://` scheme in `urlopen`) can result in access to unexpected files and expose sensitive data. In URL fetching contexts, relying on `urllib.request.urlopen` blindly can lead to Server-Side Request Forgery (SSRF) or local file read vulnerabilities if the `url` can be manipulated to use the `file://` scheme. To mitigate this, one should explicitly validate the URL scheme (e.g., ensuring it starts with `http://` or `https://`) prior to execution.

### Recommended Code Changes
To fix the `B310` Bandit warning for `urllib.urlopen` usage, add explicit validation of the URL scheme to guarantee only HTTP(S) traffic is allowed, then use `# nosec B310` to indicate the issue is intentionally suppressed after validation.

**In `./viking_girlfriend_skill/data/knowledge_reference/populate.py`:**

```python
        # Validate scheme
        if not (url.startswith("http://") or url.startswith("https://")):
            print(f"Skipping potentially unsafe URL scheme: {url}")
            continue

        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response: # nosec B310
                    data = json.loads(response.read().decode())
```

Add similar checks in the `fetch_extracts_in_batches` function.

### Subprocess Security (CWE-78)
**Severity:** LOW
**Confidence:** HIGH

Bandit scan detected the use of `subprocess` and `subprocess.run` without verifying the execution of untrusted input.

**Files & Lines:**
* `./infra/bootstrap_host.py` (Line 3, 15)

**Code Context:**
```python
14     try:
15         subprocess.run([command, "--version"], capture_output=True, check=True)
16         return True
```

### Research
According to CWE-78 (OS Command Injection), the software constructs all or part of an OS command using externally-influenced input, but it does not neutralize or incorrectly neutralizes special elements that could modify the intended OS command when it is sent to a downstream component. `subprocess.run` without `shell=True` mitigates most shell injection risks as the command is passed as an array to `execve`, but it is still good practice to manually review input arrays to ensure no unexpected executable paths or malicious command options are provided.

### Recommended Code Changes
To fix the `B404` and `B603` Bandit warnings, verify that the `command` variable is safe. If the command originates from a hardcoded list of known-safe utilities (like `docker`, `podman`, `git`), add a suppression comment `# nosec B404` to the import and `# nosec B603` to the execution.

**In `./infra/bootstrap_host.py`:**

```python
import subprocess # nosec B404

# ... later ...
    try:
        subprocess.run([command, "--version"], capture_output=True, check=True) # nosec B603
```

### Use of Assert (CWE-703)
**Severity:** LOW
**Confidence:** HIGH

Bandit scan detected multiple usages of `assert`. By default, python's assertions can be disabled globally by running the python interpreter with the `-O` flag, meaning code relying on `assert` for program control flow or security validation will be bypassed. In testing contexts, `assert` is standard and warnings are acceptable.

**Files:**
* Almost exclusively limited to testing files in `./tests/` and `./research_data/tests/`.

### Recommended Code Changes
None needed for test files. `pytest` implicitly relies on the `assert` statement to perform test verifications. Bandit flags these generically but test files are designed to run without `-O` optimizations.

### Try/Except/Pass (CWE-703)
**Severity:** LOW
**Confidence:** HIGH

Bandit scan detected blocks with `try/except/pass` which silently suppress errors.

**Files & Lines:**
* `./tests/test_cove_pipeline.py` (Line 256)
* `./tests/test_e2e_system.py` (Line 169)

### Recommended Code Changes
None needed. They are within testing files intentionally ignoring exceptions.
