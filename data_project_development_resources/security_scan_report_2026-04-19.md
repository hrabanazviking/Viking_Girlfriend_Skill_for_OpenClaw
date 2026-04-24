# Security Scan Report: 2026-04-19

## Overview
A Bandit security scan of the `viking_girlfriend_skill` codebase identified security issues that need to be addressed. The issues identified relate to the potentially insecure use of `urllib.request.urlopen`.

## Findings
The Bandit scan output highlights two occurrences of the B310 vulnerability within `viking_girlfriend_skill/data/knowledge_reference/populate.py`.

### Issue Details:
*   **Test ID:** B310 (urllib_urlopen)
*   **Confidence:** HIGH
*   **Severity:** MEDIUM
*   **Issue Text:** "Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected."
*   **Locations:**
    *   `viking_girlfriend_skill/data/knowledge_reference/populate.py`, Line 27
    *   `viking_girlfriend_skill/data/knowledge_reference/populate.py`, Line 62

## Vulnerability Analysis (B310 - `urllib.urlopen`)

### The Risk: SSRF and Path Traversal
The `urllib.request.urlopen` function is a versatile tool for opening URLs, but it supports various URL schemes beyond just `http://` and `https://`. Notably, it supports the `file://` scheme and custom FTP schemes. If user input or externally fetched data influences the URL string passed to `urlopen` without adequate validation, it introduces significant security risks:

1.  **Server-Side Request Forgery (SSRF):** An attacker might manipulate the URL to point to internal services or resources that the server has access to but should not be exposed externally. This could be used to probe internal networks, access internal APIs, or exploit vulnerabilities in internal systems.
2.  **Local File Read (Path Traversal):** An attacker could provide a URL like `file:///etc/passwd` or `file:///app/config.yml`. The application, acting on the attacker's behalf, would read the local file and potentially return its contents in the response, leading to a severe information disclosure vulnerability.

### Reference
*   Bandit Documentation on B310: [https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen](https://bandit.readthedocs.io/en/1.9.4/blacklists/blacklist_calls.html#b310-urllib-urlopen)

## Recommended Code Changes
To mitigate this risk, the application must ensure that the URL being accessed uses an expected and safe scheme (specifically, `http` or `https`) *before* the request is sent.

### Proposed Fix in `viking_girlfriend_skill/data/knowledge_reference/populate.py`

Modify both locations where `urllib.request.urlopen` is used to include an explicit scheme check. Since we know the intended targets are web APIs (specifically Wikipedia in this script), we should enforce the `https` or `http` scheme.

**Example Implementation Pattern:**

```python
# Before making the request, validate the scheme
if not url.startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme. Only HTTP(S) is permitted. URL: {url}")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    # ... process response ...
```

**Key Steps:**
1.  **Validation:** Add the `if not url.startswith(...)` check immediately before the `urllib.request.urlopen` call. This prevents arbitrary file reads or connections to unexpected protocols.
2.  **Suppression:** Once the URL is explicitly validated, we can safely append `# nosec B310` to the line containing `urllib.request.urlopen(req)`. This instructs the Bandit scanner that the potential issue has been reviewed and mitigated, preventing false positives in future scans.

### Applying the fix to `populate.py`

The changes need to be applied in `fetch_category_members` and `fetch_extracts_in_batches`.

**In `fetch_category_members` (around line 27):**
```python
        while True:
            try:
                # Add validation here
                if not url.startswith(('http://', 'https://')):
                    raise ValueError(f"Invalid URL scheme: {url}")

                req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
                with urllib.request.urlopen(req) as response: # nosec B310
                    data = json.loads(response.read().decode())
```

**In `fetch_extracts_in_batches` (around line 62):**
```python
        try:
            # Add validation here
            if not url.startswith(('http://', 'https://')):
                raise ValueError(f"Invalid URL scheme: {url}")

            req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
            with urllib.request.urlopen(req) as response: # nosec B310
                data = json.loads(response.read().decode())
```
