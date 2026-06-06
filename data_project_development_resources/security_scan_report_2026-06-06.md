# Security Scan Report

**Date**: 2026-06-06
**Scanner**: Bandit (Python SAST)
**Target**: `viking_girlfriend_skill` directory

## Findings

A static application security test (SAST) was performed using Bandit. The scan identified an issue related to the usage of URL opening functions.

### Bandit B310: Suspicious URL Open Usage

**Severity**: Medium
**Confidence**: High
**Location**: `viking_girlfriend_skill/data/knowledge_reference/populate.py` (lines 27 and 62)

**Vulnerable Code Snippet 1 (line 27):**
```python
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

**Vulnerable Code Snippet 2 (line 62):**
```python
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

#### Issue Description

The scan found an instance where `urllib.request.urlopen` is used without explicitly validating the URL scheme beforehand. According to documentation and research [1], URL open functions in Python can permit the use of local `file:` or other custom schemes in addition to standard `http:` or `https:`. If an application dynamically constructs or processes URLs without strict validation, an attacker might be able to use these unexpected schemes to access or modify unauthorized local resources, leading to a Server-Side Request Forgery (SSRF) or Path Traversal vulnerability.

While in this specific script (`populate.py`), the base URL points to `https://en.wikipedia.org/w/api.php`, the use of `urlopen` should still be hardened to prevent any potential risks if the script is modified or reused in other contexts.

#### Recommended Code Changes

To mitigate this risk, it is recommended to explicitly audit and validate the URL scheme before invoking `urllib.request.urlopen`. Specifically, verify that the URL starts with an allowed scheme, such as `http:` or `https:`.

**Suggested Fix:**
Add a validation check before the request is made.

```python
# Check if the URL scheme is permitted
if not url.startswith(("http:", "https:")):
    raise ValueError("URL must start with 'http:' or 'https:'")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response: # nosec B310
    data = json.loads(response.read().decode())
```
*(Note: `# nosec B310` can be appended to the `urlopen` line to explicitly tell Bandit to ignore this specific line in future scans, but only after the validation check has been added).*

### References
[1] Ruff Documentation - suspicious-url-open-usage (S310): https://docs.astral.sh/ruff/rules/suspicious-url-open-usage/
