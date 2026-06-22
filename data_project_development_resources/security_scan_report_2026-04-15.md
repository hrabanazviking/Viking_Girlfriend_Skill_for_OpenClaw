# Security Scan Report: 2026-04-15

## Overview
A Bandit security scan of the codebase revealed a medium-severity security issue related to `urllib.request.urlopen` calls in `viking_girlfriend_skill/data/knowledge_reference/populate.py`. The issues map to CWE-22 (Path Traversal) and CWE-918 (Server-Side Request Forgery).

## Findings
The scan flagged the following lines with a `B310` warning:
* `viking_girlfriend_skill/data/knowledge_reference/populate.py:27`
* `viking_girlfriend_skill/data/knowledge_reference/populate.py:62`

**Issue Text:** "Audit url open for permitted schemes. Allowing use of file:/ or custom schemes is often unexpected."
**Severity:** Medium
**Confidence:** High

## Research & Analysis

### CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')
* **Description:** The product uses external input to construct a pathname that is intended to identify a file or directory that is located underneath a restricted parent directory, but the product does not properly neutralize special elements within the pathname that can cause the pathname to resolve to a location that is outside of the restricted directory.
* **Impact:** An attacker can escape outside of the restricted location to access files or directories that are elsewhere on the system, which can lead to reading sensitive files, modifying files, executing unauthorized code, or denial of service.

### CWE-918: Server-Side Request Forgery (SSRF)
* **Description:** The web server receives a URL or similar request from an upstream component and retrieves the contents of this URL, but it does not sufficiently ensure that the request is being sent to the expected destination.
* **Impact:** Attackers can bypass access controls, port scan internal networks, or access documents using protocols like `file://`, `gopher://`, or `tftp://`.

### Specific Context (`urllib.request.urlopen`)
By default, `urllib.request.urlopen` supports multiple URL schemes, including `file://`. If a user can control the URL passed to this function, they might be able to read local files on the server (Local File Inclusion / Path Traversal) or make requests to internal services (SSRF).

## Recommended Mitigation
Before passing a URL to `urllib.request.urlopen`, the application must explicitly validate that the URL scheme is one of the expected, safe schemes (e.g., `http` or `https`).

### Recommended Code Changes
In `viking_girlfriend_skill/data/knowledge_reference/populate.py`, implement URL scheme validation before the `urlopen` calls:

```python
import urllib.parse
# ...
url = "..."
parsed_url = urllib.parse.urlparse(url)
if parsed_url.scheme not in ["http", "https"]:
    raise ValueError(f"Invalid URL scheme: {parsed_url.scheme}")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response: # nosec B310
# ...
```

By adding the validation check, we prevent unexpected schemes like `file://`. We then add the `# nosec B310` comment to suppress the Bandit warning, as the vulnerability has been mitigated.
