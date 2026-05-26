# Security Scan Report

**Date:** 2026-05-26

## Vulnerability Finding: B310 (Audit url open for permitted schemes)

### Overview
A Static Application Security Testing (SAST) scan utilizing Bandit was executed on the `viking_girlfriend_skill` repository. The scan identified a **MEDIUM** severity issue within the knowledge base population script.

### Affected Code
**File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`
**Lines:** 27, 62

**Code Snippet (Line 26-28):**
```python
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

**Code Snippet (Line 61-63):**
```python
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

### Research and Implications
Based on security best practices (referenced by DeepSource, StackOverflow, and Bandit documentation for BAN-B310):
- `urllib.request.urlopen` does not just handle `http://` and `https://` URLs; it can also natively resolve `ftp://` and `file://` schemes.
- Unvalidated use of this function allows an attacker who can control or manipulate the `url` parameter to access local files on the system or send requests on the internal network.
- This creates a vulnerability to **Server-Side Request Forgery (SSRF)** and **Local File Inclusion/Path Traversal**, mapping to CWE-918 and OWASP Top 10 2021 A10.
- Even if the input is considered "trusted" or hardcoded, standard automated linting will flag this call unconditionally. DeepSource and StackOverflow recommend explicit validation of the URL scheme before execution.

### Recommended Code Changes
To mitigate the risk and resolve the Bandit warning, it is recommended to explicitly validate that the URL scheme begins with `http://` or `https://`. Once validated, a `# nosec B310` comment should be added to suppress the false positive in Bandit scans.

**Proposed Fix Pattern:**
```python
if url.lower().startswith('http://') or url.lower().startswith('https://'):
    req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
    with urllib.request.urlopen(req) as response:  # nosec B310
        data = json.loads(response.read().decode())
else:
    raise ValueError(f"Disallowed URL scheme in {url}")
```

Implementing this fix ensures that `file://` or custom schemas cannot be invoked unexpectedly, preventing SSRF attacks while silencing the security scanner.
