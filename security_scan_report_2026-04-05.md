# Security Scan Report - 2026-04-05

## Overview
A security scan was conducted on the `viking_girlfriend_skill` codebase using the `bandit` SAST tool. The scan identified an issue related to Server-Side Request Forgery (SSRF) / Path Traversal vulnerabilities when opening URLs.

## Finding: B310 urllib_urlopen
The `bandit` scan detected two instances of the `B310` vulnerability in the file `viking_girlfriend_skill/data/knowledge_reference/populate.py`.

### Details
- **Issue ID**: B310
- **Severity**: Medium
- **Confidence**: High
- **Description**: Audit url open for permitted schemes. Allowing use of `file:/` or custom schemes is often unexpected and could lead to vulnerabilities.
- **Affected File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Affected Lines**: 27 and 62 (prior to fix)

### Vulnerability Explanation (SSRF & LFI)
Using `urllib.request.urlopen` (or similar functions like `urllib.urlopen`) without validating the scheme of the URL can be dangerous. If an attacker can control the URL being opened, they could supply a URL with a `file://` scheme instead of `http://` or `https://`. This would cause the application to read local files on the server (Local File Inclusion / LFI) or access internal network resources (Server-Side Request Forgery / SSRF), potentially leading to data exfiltration or deeper system compromise.

Reference: [Bandit Documentation - B310: urllib_urlopen](https://bandit.readthedocs.io/en/latest/blacklists/blacklist_calls.html#b310-urllib-urlopen)

### Recommended and Implemented Remediation
To fix this vulnerability, explicit validation of the URL scheme must be performed before the URL is opened.

The implemented fix involves:
1. Parsing the URL using `urllib.parse.urlparse`.
2. Checking that the parsed `scheme` is explicitly either `http` or `https`.
3. If the scheme is invalid, the operation is skipped/aborted.
4. Appending `# nosec B310` to the line containing `urllib.request.urlopen` to suppress the Bandit warning, as the vulnerability is now correctly mitigated.

**Code Changes in `populate.py`:**

```python
# Before
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    # ... read data ...

# After
parsed_url = urllib.parse.urlparse(url)
if parsed_url.scheme not in ('http', 'https'):
    print(f"Skipping invalid URL scheme: {url}")
    continue # or break, depending on the loop
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    # ... read data ...
```

This ensures that only external web requests over HTTP/HTTPS are allowed, mitigating the risk of LFI and SSRF.
