# Security Scan Report: 2026-03-31

## Methodology
The Viking Girlfriend Skill codebase was analyzed using **Bandit**, a Static Application Security Testing (SAST) tool designed to find common security issues in Python code.

## Executive Summary
The scan successfully evaluated the codebase and identified **two (2) Medium-severity vulnerabilities**. Both findings are related to the use of `urllib.request.urlopen()`, which inherently supports local file schemes. If malicious user input controls the URL, it could lead to Local File Inclusion (LFI) or Server-Side Request Forgery (SSRF).

---

## Detailed Findings

### 1. Insecure Use of `urllib.request.urlopen` (Bandit B310)

*   **File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
*   **Lines:** 27, 62
*   **Confidence:** HIGH
*   **Severity:** MEDIUM
*   **CWE:** [CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')](https://cwe.mitre.org/data/definitions/22.html)

#### Context
The `populate.py` script uses the standard library `urllib.request.urlopen` to fetch data from the Wikipedia API.
```python
# Line 27
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())

# Line 62
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

#### Vulnerability Analysis
The `urllib.request.urlopen` function in Python natively supports multiple URL schemes, including `http://`, `https://`, and `file://` (or `local_file://` in older vulnerabilities like CVE-2019-9948). If the `url` variable is constructed using unsanitized or user-supplied input, an attacker could supply a URL such as `file:///etc/passwd` to read arbitrary files on the local filesystem. This can lead to sensitive information disclosure. Furthermore, this behavior can be leveraged for Server-Side Request Forgery (SSRF) to access internal network resources.

While the `url` in `populate.py` is currently hardcoded to `https://en.wikipedia.org/...` (meaning the immediate exploitability is essentially zero in its current state), the SAST tool flags this as a structural risk, as future modifications to the script could introduce external input without adding proper sanitization.

### Research Data
Online research into the B310 vulnerability highlights the risks of implicit scheme handling in Python's standard URL libraries:
*   **Prisma Cloud & SonarSource Analyses:** Emphasize that `urllib`'s support for the `file://` scheme transforms what might be an intended HTTP request into a local file read vulnerability. It is explicitly recommended to validate schemes before fetching.
*   **Historical CVE Context:** Python has had multiple historical vulnerabilities related to `urllib` scheme handling (e.g., CVE-2019-9948, CVE-2011-1521), where attackers bypassed basic blocklists (like blocking `file://`) by using obscure aliases (like `local_file://`), emphasizing the need for allowlists rather than blocklists.

---

## Recommended Code Changes

To mitigate this warning and enforce defense-in-depth, the following code changes are recommended for `viking_girlfriend_skill/data/knowledge_reference/populate.py`:

**Option 1: Explicit Scheme Validation (Allowlisting)**
Before calling `urllib.request.urlopen`, explicitly verify that the URL scheme is strictly HTTPS.

```python
from urllib.parse import urlparse

# Inside the functions before urlopen:
parsed_url = urlparse(url)
if parsed_url.scheme not in ('http', 'https'):
    raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}. Only http/https are allowed.")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req, timeout=10) as response:
    # ...
```

**Option 2: Migrate to `requests` Library**
The `requests` library does not support the `file://` scheme by default, inherently mitigating this specific local file inclusion vulnerability.

```python
import requests

# Replace urllib blocks with:
response = requests.get(
    url,
    headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'},
    timeout=10
)
response.raise_for_status()
data = response.json()
```

*Note: In either option, explicitly defining a `timeout` parameter is highly recommended to prevent potential Denial of Service (DoS) situations where the request hangs indefinitely.*
