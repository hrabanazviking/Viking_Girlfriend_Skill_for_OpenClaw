# Security Scan Report: 2026-05-22

## Overview
A comprehensive static application security testing (SAST) scan was performed across the codebase using Bandit. The scan identified a security vulnerability related to insecure URL handling.

## Vulnerability Findings

### 1. Insecure Use of `urllib.request.urlopen` (Bandit B310)
- **Severity**: Medium
- **Confidence**: High
- **CWE**: CWE-22 (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'))
- **Location**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
  - Line 27: `with urllib.request.urlopen(req) as response:`

#### Description
The scan revealed that the `urllib.request.urlopen` function is being called without explicitly validating the URL scheme. By default, `urlopen` supports several schemes, including `file://`. If user-controlled or external data influences the URL parameter, an attacker could potentially read arbitrary local files from the server, resulting in a Server-Side Request Forgery (SSRF) or Local File Read attack.

#### Research and Impact Analysis
Based on research of the `B310` vulnerability and associated CVEs (such as CVE-2022-0391):
1. **Bandit B310 (urllib_urlopen)**: The Bandit documentation clearly warns against allowing the `file://` or custom schemes when opening URLs. This is considered a significant risk in applications that fetch remote resources based on potentially untrusted input.
2. **CVE-2022-0391**: A flaw in Python's `urllib.parse` module prior to versions 3.10.0b1/3.9.5 allowed attackers to inject crafted URLs with unsanitized characters (like `\r` and `\n`). While primarily an HTTP header injection/SSRF flaw, it emphasizes the importance of carefully validating and sanitizing any URL handled by the `urllib` library.
3. **SSRF Risks**: Insecure transport methods or lack of scheme validation can allow an attacker to bypass firewalls, access internal systems, or retrieve sensitive files via the `file://` protocol. Security audits strongly recommend explicitly checking that the protocol is exactly `http` or `https` and failing fast on insecure or unexpected protocols.

#### Recommended Code Changes
To resolve this issue, the URL scheme must be explicitly validated before it is processed by `urllib.request.urlopen`. Once the URL is secured against unauthorized schemes, the Bandit warning can be safely suppressed.

**Changes required in `viking_girlfriend_skill/data/knowledge_reference/populate.py`:**

```python
import urllib.request
import urllib.parse
import json
import time
import sys
from pathlib import Path

# Recommended implementation for scheme validation
def fetch_category_members(category, max_results=5000):
    # ...
        url = f"https://en.wikipedia.org/w/api.php?..."

        # Verify the URL scheme explicitly to prevent B310 SSRF/Path Traversal
        parsed_url = urllib.parse.urlparse(url)
        if parsed_url.scheme not in ("http", "https"):
            raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are permitted.")

        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                # Suppress Bandit warning after explicit validation
                with urllib.request.urlopen(req) as response:  # nosec B310
                    data = json.loads(response.read().decode())
    # ...
```

By ensuring that `urlparse(url).scheme` is restricted to `http` or `https`, the risk of processing unintended schemes like `file://` or `ftp://` is mitigated, protecting the system from SSRF and arbitrary file reading capabilities.
