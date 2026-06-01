# Security Scan Report

**Date:** 2026-06-01

## Discovered Vulnerabilities

### 1. SSRF / Path Traversal Risk (Bandit B310)
- **Location:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
  - Line 27: `with urllib.request.urlopen(req) as response:`
  - Line 62: `with urllib.request.urlopen(req) as response:`
- **Description:** The `urllib.request.urlopen` function is being called with a URL without explicit validation of the URL scheme. If user input or external data can influence the URL, it could lead to Server-Side Request Forgery (SSRF) or arbitrary local file reads using schemes like `file://` or custom schemes.
- **CWE:** CWE-918 (Server-Side Request Forgery), CWE-22 (Path Traversal)
- **Severity:** Medium
- **Confidence:** High

## Research Findings
- **Bandit B310 Documentation:** Recommends auditing URL opens for permitted schemes. `urllib` not only opens `http://` or `https://` URLs, but also `ftp://` and `file://`. Allowing `file:/` or custom schemes can be dangerous, making the application vulnerable to Server Side Request Forgery attacks or local file exposure.
- **Remediation Strategy:** Explicitly validate that the URL scheme is either `http://` or `https://` before opening the URL. After validation, append `# nosec B310` to suppress the Bandit warning.

## Recommended Code Changes
To mitigate this risk, update `viking_girlfriend_skill/data/knowledge_reference/populate.py` to validate the URL scheme before calling `urllib.request.urlopen`:

```python
# Validating scheme to mitigate B310
if not url.startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
```
