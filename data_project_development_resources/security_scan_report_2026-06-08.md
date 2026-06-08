# Security Scan Report: 2026-06-08

## Overview
A static application security testing (SAST) scan was performed using `bandit` on the codebase.

## Vulnerability Findings
**Vulnerability:** B310 (urllib_urlopen) - Audit url open for permitted schemes.
**Severity:** Medium
**Confidence:** High

### Locations
The vulnerability was identified in `viking_girlfriend_skill/data/knowledge_reference/populate.py` at the following locations:
- Line 27: `with urllib.request.urlopen(req) as response:`
- Line 62: `with urllib.request.urlopen(req) as response:`

### Explanation and Research
The `urllib.request.urlopen` function is capable of handling multiple URI schemes, not just `http` and `https`. If not properly sanitized, it can process `file://` or `ftp://` schemes.

This behavior introduces significant security risks:
1. **Local File Read:** An attacker could potentially supply a `file:///` URL (e.g., `file:///etc/passwd` or `file:///path/to/sensitive/keys`) leading the application to expose local file contents.
2. **Server-Side Request Forgery (SSRF):** Allowing arbitrary schemes and unsanitized hostnames enables attackers to make requests originating from the server to internal networks, bypassing firewalls and potentially interacting with internal systems or cloud metadata APIs (like `169.254.169.254` on AWS).

According to DeepSource (BAN-B310) and Bandit documentation, "Allowing use of file:/ or custom schemes is often unexpected." It is strongly recommended to validate that URLs start with `http` or `https` prior to execution.

## Recommended Code Changes
To mitigate this risk, explicit validation should be added to ensure the scheme of the provided URL is permitted before constructing the `Request` and calling `urlopen`.

### Proposed Fix for `viking_girlfriend_skill/data/knowledge_reference/populate.py`

Before calling `urllib.request.urlopen`, validate the scheme of the `url` variable.

```python
# Validate URL before opening it to prevent SSRF and local file access
if not (url.startswith('http://') or url.startswith('https://')):
    raise ValueError(f"Invalid URL scheme. Only HTTP and HTTPS are permitted: {url}")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
# nosec B310: URL scheme is validated above
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

Applying this check before line 26 and line 61 in `populate.py` will effectively secure the application against this specific vulnerability vector while suppressing the Bandit warning via `# nosec B310`.
