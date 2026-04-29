# Security Scan Report

**Date**: 2026-04-29
**Tool Used**: Bandit (Static Application Security Testing)

## Overview
A security scan was conducted on the entire codebase using Bandit to identify potential Python vulnerabilities. Most issues discovered were low severity (e.g., `B101` assertions used in test files, which are standard). However, two Medium severity issues related to insecure URL handling were identified.

## Issues Discovered

### Issue 1: `B310` Insecure URL Open (Medium Severity, High Confidence)
- **File**: `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line**: 27
- **Description**: Audit url open for permitted schemes. Allowing use of `file:/` or custom schemes is often unexpected. The `urllib.request.urlopen` function can open `ftp://` and `file://` URLs, potentially leading to Server Side Request Forgery (SSRF) or exposing local files on the executing machine.
- **Context**:
  ```python
  26: req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  27: with urllib.request.urlopen(req) as response:
  ```

### Issue 2: `B310` Insecure URL Open (Medium Severity, High Confidence)
- **File**: `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Line**: 62
- **Description**: Audit url open for permitted schemes. Allowing use of `file:/` or custom schemes is often unexpected. The `urllib.request.urlopen` function can open `ftp://` and `file://` URLs, potentially leading to Server Side Request Forgery (SSRF) or exposing local files on the executing machine.
- **Context**:
  ```python
  61: req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  62: with urllib.request.urlopen(req) as response:
  ```

## Recommended Code Changes

To mitigate the risk of SSRF and unauthorized file access when using `urllib.request.urlopen`, the URLs being requested should be explicitly validated to ensure they use a secure and expected scheme (e.g., `http://` or `https://`). Alternatively, you can use the `requests` library which has safer defaults.

### Option 1: URL Validation (Using `urllib`)
Add a validation check before calling `urlopen` to ensure the URL scheme is permitted.

```python
import urllib.request
import urllib.parse

# ...

# Validate URL before opening it
if url.lower().startswith(('http://', 'https://')):
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response: # nosec B310
        # Process response
        pass
else:
    raise ValueError(f"Invalid URL scheme: {url}")
```
*Note: If the code is fixed this way, the `# nosec B310` comment can be appended to explicitly tell Bandit that the URL has been validated.*

### Option 2: Use the `requests` Library
The `requests` library does not support `file://` or `ftp://` schemes by default, making it inherently safer against this specific type of SSRF.

```python
import requests

# ...

headers = {'User-Agent': 'SigridKnowledgeBuilder/1.0'}
response = requests.get(url, headers=headers)
response.raise_for_status() # Raise an exception for bad status codes
data = response.json()
# Process data
```

## Research Findings
- **Vulnerability**: CWE-918 (Server-Side Request Forgery).
- **Explanation**: `urllib.request.urlopen` does not strictly restrict protocol schemes. An attacker who can manipulate the URL could supply `file:///etc/passwd` to read local files, or `http://169.254.169.254/latest/meta-data/` to access cloud instance metadata.
- **Remediation**: Explicitly validate user-provided data and URLs used to construct requests. Ensure that the scheme is `http` or `https`. DeepSource and other static analysis tools flag this under `BAN-B310`.
