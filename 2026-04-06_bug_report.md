# Bug Report & Security Audit: 2026-04-06

## 1. Test Suite Failure: `test_federated_memory.py`

**Issue:** The test suite for `FederatedMemory` contained a `sys.exit(1)` call upon failure. When executed via `pytest`, this raised a `SystemExit` exception that aborted the entire `pytest` test session prematurely, preventing subsequent tests from running and causing a critical breakdown in CI/CD pipelines.

**Context/Research:** Pytest hooks into Python's module loading and testing framework. Using `sys.exit()` in a test suite abruptly terminates the Python process. Pytest requires tests to fail via its internal assertion rewriting or explicit `pytest.fail()` calls to properly log the failure and continue executing the rest of the test suite. Memory guidelines for this project specifically prohibit the use of `sys.exit()` in test files for this exact reason.

**Resolution:**
Replaced `sys.exit(1)` with `import pytest; pytest.fail(f"Federated memory tests failed with {FAIL} failures")` in `tests/test_federated_memory.py`.

## 2. Security Vulnerability: B310 SSRF/Path Traversal in `populate.py`

**Issue:** Bandit SAST tool identified multiple B310 Medium severity warnings in `viking_girlfriend_skill/data/knowledge_reference/populate.py`. The script was using `urllib.request.urlopen` with dynamically constructed URLs without validating the scheme. Allowing uncontrolled schemes (like `file://`) can lead to Server-Side Request Forgery (SSRF) or local file read vulnerabilities.

**Context/Research:** The `urllib.request.urlopen` function in Python natively supports multiple URL handlers, including `file://`. If an attacker can control the URL passed to this function, they can potentially read arbitrary files from the server's filesystem or make requests to internal network resources. The project memory explicitly requires validating URL schemes (e.g., ensuring they start with `http://` or `https://`) before suppressing Bandit warnings.

**Resolution:**
Added explicit validation checks to ensure the `url` starts with `https://en.wikipedia.org/` before executing `urlopen`. Included `# nosec B310` to suppress the Bandit warning post-validation.

```python
if not url.startswith("https://en.wikipedia.org/"):
    raise ValueError(f"Invalid URL scheme: {url}")
# ...
with urllib.request.urlopen(req) as response:  # nosec B310
```

## 3. General SAST Findings

A full run of `bandit` across the codebase (excluding `test_id: B101` for asserts in tests) yields no further High or Medium vulnerabilities. The codebase is currently clean of known static vulnerabilities based on the Bandit ruleset.
