# Security Scan Report: 2026-06-03

## Overview
A static application security testing (SAST) scan was performed across the repository using Bandit to identify Python vulnerabilities.

## Findings
The SAST scan uncovered two medium-severity issues related to URL opening functions.

### Issue Details: Bandit B310
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Locations**: Line 27 and Line 62
- **Description**: `Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.`

Both instances are related to the use of `urllib.request.urlopen`.

## Vulnerability Research
Research into the `Bandit B310` warning and Python's `urllib.request.urlopen` function reveals that passing untrusted URLs directly to these functions can lead to **Server-Side Request Forgery (SSRF)** vulnerabilities.

The core issue is that `urllib` natively supports multiple URL schemes. According to Bandit documentation, it advises to audit URL open functions to ensure only permitted schemes are used. Specifically, it warns that allowing the `file://` scheme or custom non-HTTP schemes could result in unexpected outcomes, such as allowing an attacker to read local system files or access internal network services that the application wouldn't normally expose.

## Recommended Code Changes
To mitigate these vulnerabilities, the URLs generated in `viking_girlfriend_skill/data/knowledge_reference/populate.py` should be explicitly validated before they are processed by the request.

### Actionable Code Changes:
1. **Scheme Validation:** Add a conditional check to ensure the URL strictly starts with `http://` or `https://` before constructing the `urllib.request.Request` object.
2. **Suppress Warning (Post-mitigation):** Once the scheme has been explicitly restricted, the Bandit warning can be safely suppressed by appending `# nosec B310` to the specific `urlopen` calls.

**Example Implementation for Line 27 & 62 (`populate.py`):**
```python
if not url.startswith(('http://', 'https://')):
    raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are permitted.")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    # ... handle response
```
This explicit validation will prevent non-HTTP schemes (like `file://` or `ftp://`) from being processed and will satisfy security auditing requirements while silencing the Bandit warnings.
