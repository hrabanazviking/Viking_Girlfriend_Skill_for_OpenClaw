# Security Scan Report - 2026-04-01

## Executive Summary
A static application security testing (SAST) scan was performed on the codebase using `bandit`. The scan identified a security vulnerability in the knowledge base population script `viking_girlfriend_skill/data/knowledge_reference/populate.py`.

## Findings

### B310: Audit URL Open for Permitted Schemes (CWE-22)
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **Location**: `viking_girlfriend_skill/data/knowledge_reference/populate.py` (Lines 27 and 62)
- **Description**: The script uses `urllib.request.urlopen` to open URLs dynamically constructed using `urllib.parse.quote`. The `bandit` tool flags this as a potential Server-Side Request Forgery (SSRF) or Local File Inclusion (LFI) vulnerability because `urllib.request.urlopen` supports arbitrary schemes, such as `file://`, `ftp://`, etc. While the URLs in this script are currently hardcoded to start with `https://en.wikipedia.org/`, dynamic inputs or future modifications could inadvertently allow other schemes to be used, leading to potential unauthorized access to local files or internal services.

## Recommended Code Changes
To mitigate this issue, the codebase should explicitly validate the URL scheme before calling `urllib.request.urlopen`.

**Example Fix:**
Before making the network request, assert or check that the URL starts with a permitted scheme (e.g., `https://`):

```python
if not url.startswith('https://'):
    raise ValueError(f"Invalid URL scheme detected. Only 'https://' is allowed. URL: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    # process response
```

Alternatively, the project could migrate to using the `requests` library, which is generally safer and less prone to unexpected scheme behavior unless explicitly configured.

## Research Data on CWE-22 and B310
- **CWE-22**: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'). This weakness can allow an attacker to read or overwrite files outside of the intended directory. In the context of URL fetching, this often manifests when `file://` schemes are unexpectedly processed.
- **Bandit B310**: The B310 plugin specifically looks for uses of `urllib.urlopen` and similar functions because they are known to automatically process `file://` URIs. If an attacker can control the URL being fetched, they can direct the application to read sensitive local files (e.g., `/etc/passwd`).
- **Mitigation Best Practices**:
  1. Validate the URL scheme before processing.
  2. Use a high-level library like `requests` which does not support `file://` by default without explicit adapter registration.
  3. Ensure that any user-supplied input used in URL construction is properly sanitized and cannot manipulate the scheme.
