# Security Scan Report

## Overview
A security scan was performed using Bandit (SAST). The following issues were found.

## Findings

### B310: blacklist
**File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Line:** 27
**Severity:** MEDIUM
**Confidence:** HIGH
**Issue:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
**CWE:** [22](https://cwe.mitre.org/data/definitions/22.html)
**Code:**
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```
**Research:**
The B310 warning from Bandit flags the usage of `urllib.request.urlopen` (or similar functions). If the URL being opened is derived from user input or is untrusted, an attacker could supply a URL with a scheme other than `http` or `https` (like `file://`, `ftp://`, or custom schemes). This can lead to severe vulnerabilities like Server-Side Request Forgery (SSRF) or Local File Inclusion (Path Traversal), where the attacker reads internal files on the system running the application.

**Recommended Code Changes:**
To resolve this issue, the code should explicitly validate that the URL scheme is either `http` or `https` before calling `urllib.request.urlopen`. Once this validation is in place, you can append a `# nosec B310` comment to the end of the line containing the `urlopen` call to suppress the Bandit warning, as the vulnerability has been mitigated.

Example mitigation:
```python
from urllib.parse import urlparse

# ...

parsed_url = urlparse(url)
if parsed_url.scheme not in ('http', 'https'):
    raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are allowed.")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    # ...
```
---

### B310: blacklist
**File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Line:** 62
**Severity:** MEDIUM
**Confidence:** HIGH
**Issue:** Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
**CWE:** [22](https://cwe.mitre.org/data/definitions/22.html)
**Code:**
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```
**Research:**
The B310 warning from Bandit flags the usage of `urllib.request.urlopen` (or similar functions). If the URL being opened is derived from user input or is untrusted, an attacker could supply a URL with a scheme other than `http` or `https` (like `file://`, `ftp://`, or custom schemes). This can lead to severe vulnerabilities like Server-Side Request Forgery (SSRF) or Local File Inclusion (Path Traversal), where the attacker reads internal files on the system running the application.

**Recommended Code Changes:**
To resolve this issue, the code should explicitly validate that the URL scheme is either `http` or `https` before calling `urllib.request.urlopen`. Once this validation is in place, you can append a `# nosec B310` comment to the end of the line containing the `urlopen` call to suppress the Bandit warning, as the vulnerability has been mitigated.

Example mitigation:
```python
from urllib.parse import urlparse

# ...

parsed_url = urlparse(url)
if parsed_url.scheme not in ('http', 'https'):
    raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are allowed.")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    # ...
```
---
