# Security Scan Report: 2026-05-26

## Overview
A static application security testing (SAST) scan was performed using Bandit. This report outlines the discovered vulnerabilities and recommends remediation steps.

## Findings

### 1. Medium Severity: B310 (urllib_urlopen)
**Location:** `viking_girlfriend_skill/data/knowledge_reference/populate.py` (lines 27, 62)
**Confidence:** High
**Issue Text:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.

**Vulnerable Code Snippets:**
```python
# Line 27
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

```python
# Line 62
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

## Research Data
According to the [Bandit B310 documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen):
- **Issue:** Using functions like `urllib.request.urlopen` with unvalidated input or without verifying the URL scheme can allow an attacker to supply a `file://` scheme or custom schemes.
- **Impact:** This might lead to unexpected access to the local file system (Path Traversal) or enable Server-Side Request Forgery (SSRF) attacks if an attacker can manipulate the URL.

## Recommended Code Changes
To mitigate the B310 vulnerability, it is necessary to validate the URL scheme before calling `urllib.request.urlopen`. Ensure that only the `http` and `https` schemes are permitted. Once validated, you can safely ignore the Bandit warning on that specific line by appending `# nosec B310`.

**Recommended Fix (`viking_girlfriend_skill/data/knowledge_reference/populate.py`):**

```python
# Add this import at the top of the file if not present
from urllib.parse import urlparse

# Update the fetch code blocks
parsed_url = urlparse(url)
if parsed_url.scheme not in ('http', 'https'):
    raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    data = json.loads(response.read().decode())
```
