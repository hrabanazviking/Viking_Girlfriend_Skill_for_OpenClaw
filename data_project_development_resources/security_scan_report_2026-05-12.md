# Security Scan Report: 2026-05-12

## Executive Summary
A static application security testing (SAST) scan was performed using Bandit. The scan identified a Medium-severity issue related to the use of `urllib.request.urlopen` in the project's data population scripts.

## Findings

### Vulnerability: Server-Side Request Forgery (SSRF) / Path Traversal Risk (Bandit B310)

**Severity:** Medium
**Location:**
- `viking_girlfriend_skill/data/knowledge_reference/populate.py:27`
- `viking_girlfriend_skill/data/knowledge_reference/populate.py:62`

**Description:**
The script uses `urllib.request.urlopen` to fetch data from Wikipedia's API. The URL is passed directly to the function without prior validation of the URL scheme. While the current usage constructs the URL using a hardcoded base (`https://en.wikipedia.org/`), using `urllib.request.urlopen` without scheme validation is flagged by security tools because it inherently supports potentially dangerous schemes like `file://` and `ftp://`. If the URL construction logic is ever modified to accept user input or external data, it could lead to a Server-Side Request Forgery (SSRF) or allow an attacker to read local files on the server executing the script.

**Context & Research:**
- According to Bandit's documentation for [B310: urllib_urlopen](https://bandit.readthedocs.io/en/1.7.2/blacklists/blacklist_calls.html#b310-urllib-urlopen), the tool audits `urllib.urlopen` for permitted schemes because allowing use of `file:/` or custom schemes is often unexpected and dangerous.
- DeepSource's advisory on [BAN-B310](https://deepsource.com/directory/python/issues/BAN-B310) highlights that `urllib` not only opens `http://` or `https://` URLs, but also `ftp://` and `file://`. Opening local files on the executing machine is a security risk if the URL can be manipulated. This makes the application vulnerable to Server Side Request Forgery (SSRF) attacks, corresponding to [CWE-918](https://cwe.mitre.org/data/definitions/918.html).

## Recommended Code Changes

To address this issue, we should implement a strict validation check on the URL scheme before calling `urllib.request.urlopen`. Once the URL is validated, we can append a `# nosec B310` comment to the `urlopen` line to explicitly suppress the Bandit warning, indicating that the risk has been mitigated.

**Example Fix for `viking_girlfriend_skill/data/knowledge_reference/populate.py`:**

```python
<<<<<<< SEARCH
        while True:
            try:
                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:
                    data = json.loads(response.read().decode())
=======
        while True:
            try:
                # Explicitly validate the URL scheme to prevent SSRF and B310 Path Traversal
                if not url.startswith('http://') and not url.startswith('https://'):
                    raise ValueError(f"Invalid URL scheme: {url}")

                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response:  # nosec B310
                    data = json.loads(response.read().decode())
>>>>>>> REPLACE
```

```python
<<<<<<< SEARCH
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                pages = data['query']['pages']
=======
        try:
            # Explicitly validate the URL scheme to prevent SSRF and B310 Path Traversal
            if not url.startswith('http://') and not url.startswith('https://'):
                raise ValueError(f"Invalid URL scheme: {url}")

            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response:  # nosec B310
                data = json.loads(response.read().decode())
                pages = data['query']['pages']
>>>>>>> REPLACE
```

Implementing these changes will resolve the Bandit warnings while ensuring the code is resilient against potential URL manipulation vulnerabilities.
