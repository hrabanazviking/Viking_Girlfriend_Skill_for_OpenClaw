# Security Scan Report - 2026-03-26

## Overview
This report details the findings from a recent security scan of the codebase using Bandit.
The primary tool used for identifying these vulnerabilities was `bandit -r viking_girlfriend_skill/ -f json`.

## Findings
Found 2 potential security issues.

### Issue 1: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. (B310)
- **Severity:** MEDIUM
- **Confidence:** HIGH
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py:27`
- **CWE:** [CWE-918: Server-Side Request Forgery (SSRF)](https://cwe.mitre.org/data/definitions/918.html)
  - **Description:** Description






The web server receives a URL or similar request from an upstream component and retrieves the contents of this URL, but it does not sufficiently ensure that the request is being sent to the expected destination....
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen
- **Code Snippet:**
```python
26                 req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
27                 with urllib.request.urlopen(req) as response:
28                     data = json.loads(response.read().decode())
```

#### Analysis & Recommendations
The `urllib.request.urlopen` function is vulnerable to Server-Side Request Forgery (SSRF) and local file inclusion (LFI) / file disclosure if the URL is user-controllable and can specify custom schemes like `file://`.
In `viking_girlfriend_skill/data/knowledge_reference/populate.py`, the URLs are constructed, but using `urllib.request.urlopen` without scheme validation is a security risk. If an attacker could influence the URL parameters (even indirectly), they might be able to exfiltrate local files or make the server perform requests to internal resources.

**Recommended Code Changes:**
Option 1 (Best Practice): Switch to using the `requests` library. `requests` does not support `file://` or custom schemes out of the box, mitigating this risk.
```python
import requests
# ...
url = f"https://en.wikipedia.org/w/api.php?..."
try:
    response = requests.get(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    response.raise_for_status() # Raise an exception for bad status codes
    data = response.json()
    # ...
except requests.RequestException as e:
    print(f"Request failed: {e}")
```

Option 2 (If keeping `urllib`): Explicitly validate the URL scheme.
```python
from urllib.parse import urlparse
# ...
parsed_url = urlparse(url)
if parsed_url.scheme not in ('http', 'https'):
    raise ValueError("Only HTTP/HTTPS URLs are allowed.")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    # ...
```

### Issue 2: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected. (B310)
- **Severity:** MEDIUM
- **Confidence:** HIGH
- **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py:62`
- **CWE:** [CWE-918: Server-Side Request Forgery (SSRF)](https://cwe.mitre.org/data/definitions/918.html)
  - **Description:** Description






The web server receives a URL or similar request from an upstream component and retrieves the contents of this URL, but it does not sufficiently ensure that the request is being sent to the expected destination....
- **More Info:** https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen
- **Code Snippet:**
```python
61             req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
62             with urllib.request.urlopen(req) as response:
63                 data = json.loads(response.read().decode())
```

#### Analysis & Recommendations
The `urllib.request.urlopen` function is vulnerable to Server-Side Request Forgery (SSRF) and local file inclusion (LFI) / file disclosure if the URL is user-controllable and can specify custom schemes like `file://`.
In `viking_girlfriend_skill/data/knowledge_reference/populate.py`, the URLs are constructed, but using `urllib.request.urlopen` without scheme validation is a security risk. If an attacker could influence the URL parameters (even indirectly), they might be able to exfiltrate local files or make the server perform requests to internal resources.

**Recommended Code Changes:**
Option 1 (Best Practice): Switch to using the `requests` library. `requests` does not support `file://` or custom schemes out of the box, mitigating this risk.
```python
import requests
# ...
url = f"https://en.wikipedia.org/w/api.php?..."
try:
    response = requests.get(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    response.raise_for_status() # Raise an exception for bad status codes
    data = response.json()
    # ...
except requests.RequestException as e:
    print(f"Request failed: {e}")
```

Option 2 (If keeping `urllib`): Explicitly validate the URL scheme.
```python
from urllib.parse import urlparse
# ...
parsed_url = urlparse(url)
if parsed_url.scheme not in ('http', 'https'):
    raise ValueError("Only HTTP/HTTPS URLs are allowed.")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    # ...
```
