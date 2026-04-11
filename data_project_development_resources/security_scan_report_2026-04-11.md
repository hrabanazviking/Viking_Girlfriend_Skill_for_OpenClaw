# Security Scan Report: 2026-04-11

## Overview
A Bandit security scan was performed on the `viking_girlfriend_skill` codebase to identify potential vulnerabilities. The scan identified a Medium severity issue related to the use of `urllib.request.urlopen`.

## Findings

### B310: urllib_urlopen (SSRF / Path Traversal)
- **Severity:** Medium
- **Confidence:** High
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Lines Affected:** 27, 62 (Prior to fix)
- **Issue Text:** "Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected."

## Vulnerability Research
According to the Bandit documentation (https://bandit.readthedocs.io/en/1.7.8/blacklists/blacklist_calls.html#b310-urllib-urlopen), the use of functions like `urllib.request.urlopen` can be dangerous if the URL being opened is derived from untrusted input or lacks explicit scheme validation.

Specifically, allowing custom schemes such as `file://` can permit an attacker to perform a Path Traversal (CWE-22) attack or Server-Side Request Forgery (SSRF). By providing a `file://` URI, an attacker might trick the application into reading local files from the server's filesystem, exposing sensitive data. While the URLs in `populate.py` were hardcoded Wikipedia API endpoints, the static analysis tool appropriately flags this usage as a best-practice violation, requiring explicit validation to defend against potential future regressions where inputs might become dynamic.

### CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
Path traversal vulnerabilities occur when an application uses external input to construct a pathname intended to identify a file or directory but does not properly neutralize special elements. In the context of `urllib.urlopen`, if an attacker controls the URL scheme and uses `file://`, they can bypass expected network requests and access arbitrary files on the local filesystem.

## Implemented Fix
To mitigate this finding and adhere to secure coding practices, explicit URL scheme validation was added before the `urllib.request.urlopen` calls in `populate.py`.

The code was modified as follows:
```python
if not url.startswith('http://') and not url.startswith('https://'):
    raise ValueError("Invalid URL scheme")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
```

This ensures that only `http://` or `https://` requests are processed, effectively preventing local file access via the `file://` scheme. The `# nosec B310` comment was added to suppress the Bandit warning, signaling that the vulnerability has been acknowledged and mitigated via validation.

## Conclusion
The B310 vulnerability has been fully resolved. A subsequent Bandit scan verified that the `viking_girlfriend_skill` codebase is now clean of Medium and High severity security issues (excluding informational B101 assertions).
