# Security Scan Data - 2026-04-03

## Overview
A security scan using the `bandit` SAST tool was executed on the `viking_girlfriend_skill` codebase on 2026-04-03. This document summarizes the findings, provides research into the identified issues, and recommends necessary code modifications to remediate the vulnerabilities.

## Scan Findings
The Bandit scan identified two instances of the `B310` vulnerability in `viking_girlfriend_skill/data/knowledge_reference/populate.py`.

*   **Tool:** Bandit
*   **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
*   **Lines:** 27 and 62
*   **Test ID:** B310
*   **Issue Confidence:** HIGH
*   **Issue Severity:** MEDIUM
*   **CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'))
*   **Issue Text:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

## Vulnerability Research: B310 (urllib_urlopen)
### Description
The `B310` vulnerability occurs when Python's `urllib.request.urlopen` (or similar URL open functions) is used without explicitly validating the URL scheme.

### Risks
Functions like `urlopen` are capable of handling various URL schemes beyond `http://` and `https://`. Crucially, they can process the `file://` scheme. If an application constructs a URL using external, untrusted input and passes it directly to `urlopen` without validation, an attacker could supply a `file://` URL pointing to sensitive local files (e.g., `file:///etc/passwd`). This could lead to a Server-Side Request Forgery (SSRF) or an arbitrary local file read vulnerability, allowing the attacker to access unauthorized resources on the server.

### Context within the Codebase
In `populate.py`, the URLs are constructed using string formatting:
*   `url = f"https://en.wikipedia.org/w/api.php?..."`
While the base URL is hardcoded to `https://en.wikipedia.org`, mitigating the immediate risk of a user supplying a completely arbitrary `file://` URL, the use of `urlopen` without explicit scheme validation is still flagged by SAST tools as a bad practice. It is safer to explicitly enforce the expected schemes.

## Recommended Code Changes
To remediate the `B310` vulnerability and adhere to security best practices, the URL scheme must be explicitly validated before the `urllib.request.urlopen` call.

The code in `viking_girlfriend_skill/data/knowledge_reference/populate.py` should be modified to assert or verify that the URL begins with `https://` (or `http://` if necessary, though `https://` is preferred).

**Proposed Modification:**
```python
# Before using urlopen, validate the scheme
if not url.startswith('https://') and not url.startswith('http://'):
    raise ValueError(f"Invalid URL scheme. Only HTTP and HTTPS are allowed: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    # ...
```
This check should be applied prior to both `urlopen` calls in the file (in `fetch_category_members` and `fetch_extracts_in_batches`).
