# Security Scan Report: 2026-05-22

## Overview
A static application security testing (SAST) scan was performed using Bandit.

## Findings

### B310: urllib_urlopen
- **Severity**: MEDIUM
- **Location**: `viking_girlfriend_skill/data/knowledge_reference/populate.py` (lines 27 and 62)
- **Description**: The `urllib.request.urlopen` function is used to open URLs. By default, it allows any scheme, including `file://` or custom schemes. This could lead to a Server-Side Request Forgery (SSRF) or Path Traversal vulnerability if the URL is user-controlled.
- **Reference**: [Bandit Documentation on B310](https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html#b310-urllib-urlopen)

## Research Findings
According to the Bandit documentation, `urllib.urlopen` and similar functions should be audited for permitted schemes. Allowing the use of `file://` or other custom schemes is often unexpected and can be dangerous, potentially allowing local file reading (Path Traversal) or internal network requests (SSRF).

## Recommended Code Changes
To remediate this issue in `populate.py`, the URL scheme should be explicitly validated before opening it. If it's a known static target like Wikipedia, we should enforce the `https://` scheme.

```python
        url = f"https://en.wikipedia.org/w/api.php?..."

        while True:
            try:
                if not url.startswith('https://') and not url.startswith('http://'):
                    raise ValueError(f"Invalid URL scheme: {url}")

                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response: # nosec B310
                    # ...
```
This validation must be done before the request execution, and then we can append `# nosec B310` to suppress the Bandit warning. Note that per user request, we are only reporting on this, not modifying the file.
