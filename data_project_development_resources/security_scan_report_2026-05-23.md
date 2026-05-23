# Security Scan Report

**Date:** 2026-05-23
**Scanner:** Bandit

## Overview

A Static Application Security Testing (SAST) scan was performed using Bandit. The scan identified two types of vulnerabilities within the codebase:

1.  **Low Severity:** Use of `assert` statements outside of a dedicated testing environment (B101).
2.  **Medium Severity:** Use of an insecure URL open method from `urllib` (B310).

## Vulnerability Details

### 1. B101: `assert_used`

**Severity:** LOW
**Confidence:** HIGH

**Description:**
Bandit identified the use of `assert` statements in several test files.

**Affected Files & Lines:**
- `./tests/test_vordur_trigger.py` (Lines 197, 204, 217, 228)
- `./tests/test_wyrd_vitality_modulation.py` (Lines 21, 27, 35, 43, 51, 57, 65)

**Analysis:**
While `assert` statements are commonly used in test suites (especially with pytest), the Python runtime ignores them when compiled to optimized byte code (using the `-O` flag). If a system relies on `assert` for critical validations outside of a testing context, those validations can be bypassed. In this case, the `assert` statements are strictly located within the `./tests/` directory.

**Recommended Code Changes:**
Because these are within test files and pytest is the test runner, the use of `assert` is standard and expected. However, to silence the Bandit warnings or align with more robust validation if these were ever moved outside testing, the tests could be rewritten to use `pytest.fail()` or raise specific exceptions like `AssertionError` explicitly, though standard `assert` is preferred for pytest.

For now, these can be safely ignored or suppressed via `# nosec B101` if strict zero-warning compliance is required.

---

### 2. B310: `urllib_urlopen`

**Severity:** MEDIUM
**Confidence:** HIGH

**Description:**
Bandit detected the use of `urllib.request.urlopen()`, which can be vulnerable to Server-Side Request Forgery (SSRF) and local file inclusion if the URL scheme is not validated.

**Affected Files & Lines:**
- `./viking_girlfriend_skill/data/knowledge_reference/populate.py` (Lines 27, 62)

**Analysis & Research:**
According to DeepSource (BAN-B310):
> `urllib` not only opens `http://` or `https://` URLs, but also `ftp://` and `file://`. With this, it might be possible to open local files on the executing machine which might be a security risk if the URL to open can be manipulated by an external user.

The `urllib.request` module's `urlopen` function can open `file://` URLs. This is usually not intended and makes the application vulnerable to Server Side Request Forgery (SSRF) attacks or local file access if user input can dictate the URL.

In the `populate.py` file, the URLs being constructed are hardcoded to start with `https://en.wikipedia.org/w/api.php?`, but they dynamically include `current_cat` and `batch` parameters which are URL-encoded. Since the scheme is fixed in the string literal, it is not currently exploitable to change the scheme to `file://`. However, best practices dictate explicit validation or suppression.

**Recommended Code Changes:**
To resolve this issue and follow secure coding practices, the URL should be explicitly validated to ensure it starts with an allowed scheme (e.g., `http` or `https`) before calling `urlopen`. Furthermore, to suppress the Bandit warning since we are validating it, we can append `# nosec B310` to the `urlopen` line.

**Example Fix:**

```python
# Before
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    # ...

# After (Recommended)
if not url.lower().startswith(('http://', 'https://')):
    raise ValueError("Invalid URL scheme.")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    # ...
```

By explicitly validating the scheme, we mitigate the potential SSRF/Local File access vector described in the B310 documentation.
