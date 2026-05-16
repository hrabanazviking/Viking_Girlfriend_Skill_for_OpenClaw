# Security Scan Report: 2026-05-16

## Executive Summary
A static application security testing (SAST) scan was performed using Bandit on the `viking_girlfriend_skill` directory. The scan identified a security vulnerability related to the use of `urllib.request.urlopen`.

## Findings

### B310: Audit url open for permitted schemes
- **Severity**: Medium
- **Confidence**: High
- **CWE**: [CWE-22](https://cwe.mitre.org/data/definitions/22.html) (Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal'))
- **File**: `viking_girlfriend_skill/data/knowledge_reference/populate.py`
- **Lines**: 27, 62

#### Description
The Bandit B310 rule flags the use of `urllib.request.urlopen` because it not only opens `http://` or `https://` URLs, but also `ftp://` and `file://`. If the URL passed to `urlopen` is influenced by user input, an attacker could potentially read local files on the executing machine (e.g., using a `file://` URI), leading to Server Side Request Forgery (SSRF) or path traversal vulnerabilities.

According to DeepSource (https://deepsource.com/directory/python/issues/BAN-B310):
> "urllib not only opens http:// or https:// URLs, but also ftp:// and file://. With this, it might be possible to open local files on the executing machine which might be a security risk if the URL to open can be manipulated by an external user... You are yourself responsible for validating the URL before opening it with urllib."

#### Recommended Remediation
Although the URLs in `populate.py` appear to be hardcoded to `https://en.wikipedia.org/...` with some parameters safely URL-encoded (`urllib.parse.quote()`), it is a security best practice to explicitly validate the URL scheme before making the request.

Here is the recommended code change for both occurrences in `viking_girlfriend_skill/data/knowledge_reference/populate.py`:

**Before:**
```python
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:
    data = json.loads(response.read().decode())
```

**After:**
```python
if not url.lower().startswith(('http://', 'https://')):
    raise ValueError(f"Invalid URL scheme: {url}")
req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response: # nosec B310
    data = json.loads(response.read().decode())
```

**Note:** The `# nosec B310` comment is appended to suppress the Bandit warning after explicit validation has been implemented, signaling that the potential risk has been mitigated.
