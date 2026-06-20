# Security Scan Report - 2026-04-12

## Overview
A Bandit SAST scan identified two Medium-severity, High-confidence B310 vulnerabilities within `viking_girlfriend_skill/data/knowledge_reference/populate.py`. These relate to the insecure use of `urllib.request.urlopen`.

## Finding Details
**Tool:** Bandit
**Test ID:** B310 (blacklist_calls)
**CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'))
**File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Lines:** 27, 62
**Issue Text:** "Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected."

## Vulnerability Research
Based on the provided link to CWE-22 and further context:
- **CWE-22 Details:** The weakness "Path Traversal" involves software using external input to construct a pathname that is intended to identify a file or directory underneath a restricted parent directory. If not properly neutralized, an attacker can use special elements (like `../` or `file://` schemes) to access files or directories outside of the intended restricted directory.
- **Risk in `urllib.request.urlopen`:** By default, `urllib.request.urlopen` supports multiple schemes, including `file://`. If the URL provided to `urlopen` can be influenced by malicious input, an attacker could force the application to read arbitrary local files on the system instead of making a web request.
- **Common Consequences:** Can include reading sensitive files (Confidentiality impact), executing unauthorized code, modifying files, or causing Denial of Service (DoS) crashes if an attacker controls the targeted resource.
- **Potential Mitigations:** Validate input strings against strict allowlists (e.g. limiting valid characters or starting strings). Validate the scheme specifically when making HTTP requests.

## Recommended Code Changes
To mitigate the B310 risk, we must enforce that the URL scheme is strictly `http://` or `https://` before attempting to open the URL. This prevents an attacker from supplying a URL that starts with `file://`, `ftp://`, or other unexpected protocols. Once this validation is in place, we can safely append `# nosec B310` to the `urlopen` call to suppress the Bandit warning.

**Proposed Fix in `populate.py`:**
Before `urllib.request.urlopen(req)` is called (on lines 27 and 62), add a validation check:
```python
if not (url.startswith('http://') or url.startswith('https://')):
    raise ValueError(f"Invalid URL scheme: {url}")
```
And modify the `urlopen` line to include the Bandit exception:
```python
with urllib.request.urlopen(req) as response:  # nosec B310
```
