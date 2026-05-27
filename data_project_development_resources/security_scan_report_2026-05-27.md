# Security Scan Report: 2026-05-27

## Overview
A static application security test (SAST) was performed using Bandit. Several potential vulnerabilities were identified. This report focuses specifically on the most severe finding regarding the insecure use of the `urllib` library.

## Finding: B310 - Insecure use of `urllib.request.urlopen`

### Details
- **Issue**: Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected.
- **Severity**: MEDIUM
- **Confidence**: HIGH
- **CWE ID**: [CWE-22](https://cwe.mitre.org/data/definitions/22.html)
- **File**: `./viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Lines**: 27, 62

```python
# Lines 26-28
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

### Research and Analysis
The `urllib.request.urlopen` function is capable of fetching resources across various protocols, not just `http://` or `https://`. Crucially, it supports `file://` and `ftp://` schemes.

If an application allows an external user (or an untrusted source) to dictate the `url` parameter passed to `urlopen`, it creates a severe vulnerability known as **Server-Side Request Forgery (SSRF)**.

*   **Local File Disclosure**: An attacker could provide a URL like `file:///etc/passwd` or `file:///home/user/.aws/credentials`. The server process running the Python script would then read these local files and potentially return their contents to the attacker.
*   **Internal Network Scanning**: Attackers can probe the internal network (which is otherwise inaccessible from the outside) by requesting URLs like `http://192.168.1.x:8080/` or cloud metadata services like `http://169.254.169.254/latest/meta-data/` (common in AWS environments).

While the Bandit scan maps this to **CWE-22** (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')), the core risk mechanism when dealing with remote URLs is SSRF (often associated with CWE-918, though Bandit specifically flags the `urllib` behavior under its B310 test).

### Recommended Code Changes
To mitigate this vulnerability, it is essential to validate that the URL provided to `urlopen` uses an expected and secure scheme (e.g., `http` or `https`) before making the request.

**Proposed Implementation:**

```python
<<<<<<< SEARCH
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
=======
                if not url.lower().startswith(('http://', 'https://')):
                    raise ValueError("Invalid URL scheme.")
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
                    data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

*Note: The `# nosec B310` comment is added after implementing the validation logic to signal to Bandit that the risk has been acknowledged and mitigated, silencing future warnings for this specific line.*

## Additional Findings
- **B404 & B603**: Informational warnings regarding the import and use of the `subprocess` module in `infra/bootstrap_host.py` (lines 3, 15). These should be reviewed to ensure that no untrusted input is passed into the shell commands, though they are currently marked as LOW severity. If deemed safe for local execution, they can be suppressed with `# nosec B404` and `# nosec B603`.
