# Security Scan Report: 2026-03-23

## Executive Summary
A static application security testing (SAST) scan was performed across the codebase using `bandit` to identify potential security vulnerabilities in Python code.

The scan successfully completed, evaluating over 34,000 lines of code.

### Scan Metrics:
* **Total High Severity Issues:** 0
* **Total Medium Severity Issues:** 2
* **Total Low Severity Issues:** 741

## Identified Vulnerabilities

### 1. `[B310:blacklist]` Audit url open for permitted schemes
* **Severity:** Medium
* **Confidence:** High
* **CWE:** CWE-22 (Improper Limitation of a Pathname to a Restricted Directory 'Path Traversal')
* **Location:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
  * Line 27: `with urllib.request.urlopen(req) as response:`
  * Line 62: `with urllib.request.urlopen(req) as response:`

#### Details and Research
Bandit rule **B310** flags the use of `urllib.request.urlopen` (and similar functions) because they support not only standard HTTP/HTTPS schemes, but also custom schemes and the `file://` scheme. If an application accepts user-controlled input to build the URL passed to `urlopen`, an attacker could supply a URL like `file:///etc/passwd` or `file:///C:/Windows/System32/drivers/etc/hosts`.

If the application reads this file and exposes the output back to the attacker, it results in a Local File Inclusion (LFI) or Path Traversal vulnerability (CWE-22). In other contexts, this could also be used for Server-Side Request Forgery (SSRF), where the server is tricked into making requests to internal network resources.

While in `populate.py` the URLs appear to be hardcoded to `https://en.wikipedia.org/`, the use of `urlopen` without explicit scheme validation is considered a bad practice and is flagged by SAST tools.

**More info:** [Bandit B310 Documentation](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen)

#### Recommended Code Changes
To remediate this finding and improve the code's resilience, you must validate that the URL scheme is strictly limited to `http` or `https` before passing it to `urlopen`.

Alternatively, migrating to the popular `requests` library is recommended, as it defaults to handling HTTP/HTTPS and is less susceptible to `file://` scheme abuse by default, while also providing a cleaner API.

**Option 1: Scheme Validation (Using `urllib`)**
Modify the code to check the scheme before making the request:

```python
import urllib.request
import urllib.parse
from urllib.parse import urlparse
import json

def safe_urlopen(url, headers=None):
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https'):
        raise ValueError(f"Invalid URL scheme: {parsed.scheme}. Only HTTP and HTTPS are allowed.")

    req_headers = headers or {'User-Agent': 'SigridKnowledgeBuilder/1.0'}
    req = urllib.request.Request(url, headers=req_headers)
    return urllib.request.urlopen(req)

# Example Usage in populate.py:
# with safe_urlopen(url) as response:
#     data = json.loads(response.read().decode())
```

**Option 2: Migrate to `requests` Library (Recommended)**
If the `requests` library is available in the environment (`pip install requests`), it simplifies the code significantly:

```python
import requests
import json

# Example Usage in populate.py:
# response = requests.get(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
# response.raise_for_status() # Raise exception for bad status codes
# data = response.json()
```

By applying either of these changes, the `bandit` B310 warnings will be resolved, and the code will be more secure against potential SSRF and LFI attacks if URLs ever become dynamic or user-controlled in the future.