# Security Scan Report: 2026-05-31

## Overview
A Bandit SAST static security scan was executed against the `viking_girlfriend_skill` directory. The results have been analyzed, and the findings are detailed below along with research and recommended code changes.

## Findings

### 1. B310: Audit url open for permitted schemes (CWE-22)
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **Location**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
  - Line 27: `with urllib.request.urlopen(req) as response:`
  - Line 62: `with urllib.request.urlopen(req) as response:`

#### Analysis & Research
The `urllib.request.urlopen` function allows for various schemes like `http`, `https`, `ftp`, and `file`. If a URL is dynamically constructed from untrusted input, an attacker can use a `file://` scheme to access arbitrary local files or construct paths to perform Server-Side Request Forgery (SSRF) and Path Traversal (CWE-22) attacks.

Even though the base URL (`https://en.wikipedia.org/w/api.php`) in this script is hardcoded, `urllib.parse.quote` might not fully prevent all malicious behavior if the input logic is manipulated. Security tools like Bandit will flag any use of `urllib.request.urlopen` if the URL is not explicitly verified or if a safer alternative like `requests` is not used.

#### Recommended Code Change
Explicitly validate that the URL scheme begins with `https://` before opening it, and append a `# nosec B310` comment so Bandit knows it has been checked. Alternatively, migrate the code to use the `requests` library.

**Example Fix (Explicit Validation & Nosec):**
```python
# Before
url = f"https://en.wikipedia.org/w/api.php?..."
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:

# After
url = f"https://en.wikipedia.org/w/api.php?..."
if not url.startswith("https://"):
    raise ValueError("Invalid URL scheme.")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
```

### 2. B324: Use of weak MD5 hash for security (CWE-327)
- **Severity**: HIGH
- **Confidence**: HIGH
- **Location**: `viking_girlfriend_skill/scripts/vordur.py`
  - Line 441: `hashlib.md5(claim_text.encode("utf-8")).hexdigest()`
  - Line 442: `hashlib.md5(chunk_text.encode("utf-8")).hexdigest()`

#### Analysis & Research
The MD5 cryptographic hash function is considered weak and has been broken (collisions can be generated). While it is often used for non-cryptographic purposes like cache keys (as is the case in `vordur.py`), security scanners will flag it.

#### Recommended Code Change
Update the MD5 usage to explicitly mark it as not used for security by passing `usedforsecurity=False` (available in Python 3.9+). The code currently has `# nosec B324` but the implementation still triggers some warnings, or it's cleaner to just fix the logic.

**Example Fix:**
```python
hashlib.md5(claim_text.encode("utf-8"), usedforsecurity=False).hexdigest(),  # nosec B324
hashlib.md5(chunk_text.encode("utf-8"), usedforsecurity=False).hexdigest(),  # nosec B324
```

### 3. B110: Try, Except, Pass detected (CWE-703)
- **Severity**: LOW
- **Confidence**: HIGH
- **Location**: Numerous locations across the codebase including `main.py`, `vordur.py`, `security.py`, `mimir_well.py`, `tests/test_cove_pipeline.py`, etc.

#### Analysis & Research
Catching `Exception` and doing nothing (`pass`) silently swallows all errors. This is dangerous because it hides state corruption, makes debugging difficult, and could allow an application to continue in an inconsistent state.

#### Recommended Code Change
Replace `pass` with a logging statement or catch a more specific exception. Where `pass` is strictly intended (such as in specific test setup/teardown), append `# nosec B110`.

**Example Fix:**
```python
# Before
try:
    _vordur = get_vordur()
except Exception:
    pass

# After
try:
    _vordur = get_vordur()
except Exception as e:
    logger.warning("Vordur initialization failed: %s", e)
```

### 4. B101: Use of assert detected (CWE-703)
- **Severity**: LOW
- **Confidence**: HIGH
- **Location**: ~745 instances, primarily in the `tests/` directory.

#### Analysis & Research
`assert` statements are removed when Python is compiled to optimized byte code (using the `-O` flag). Using assertions for control flow or data validation in production code can lead to vulnerabilities. However, they are expected and standard in test suites (`pytest`).

#### Recommended Code Change
No code changes are necessary for test files as this is standard `pytest` behavior. Ensure no `assert` statements are used for business logic in the `viking_girlfriend_skill/scripts/` directory.

### 5. B404 and B603: subprocess module (CWE-78)
- **Severity**: LOW
- **Confidence**: HIGH
- **Location**: `infra/bootstrap_host.py`
  - Line 3: `import subprocess`
  - Line 15: `subprocess.run([command, "--version"], capture_output=True, check=True)`

#### Analysis & Research
The `subprocess` module can be used to execute arbitrary OS commands. If inputs to `subprocess` functions are not properly sanitized, it can lead to OS Command Injection. In `bootstrap_host.py`, the `command` variable comes from hardcoded strings ("podman", "docker", "nvidia-smi"), so it is safe.

#### Recommended Code Change
Append `# nosec B404` and `# nosec B603` to the respective lines to document that this is safe and suppress the warnings.

**Example Fix:**
```python
import subprocess  # nosec B404
...
subprocess.run([command, "--version"], capture_output=True, check=True)  # nosec B603
```
