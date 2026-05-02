# Security Scan Report: 2026-05-02

## Overview
A static application security testing (SAST) scan was performed on the `viking_girlfriend_skill` codebase using **Bandit**.

## Findings
The scan identified two issues related to insecure URL fetching, both flagged with **MEDIUM severity** and **HIGH confidence**.

### Issue Details

- **Tool Used:** Bandit
- **Vulnerability:** SSRF / Path Traversal (Bandit test ID: **B310**)
- **CWE:** [CWE-22: Improper Limitation of a Pathname to a Restricted Directory ('Path Traversal')](https://cwe.mitre.org/data/definitions/22.html)
- **Affected File:** `viking_girlfriend_skill/data/knowledge_reference/populate.py`

#### Finding 1
- **Line:** 27
- **Code:**
  ```python
  req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  with urllib.request.urlopen(req) as response:
      data = json.loads(response.read().decode())
  ```
- **Description:** `urllib.request.urlopen` is called without validating the URL scheme.

#### Finding 2
- **Line:** 62
- **Code:**
  ```python
  req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
  with urllib.request.urlopen(req) as response:
      data = json.loads(response.read().decode())
  ```
- **Description:** `urllib.request.urlopen` is called without validating the URL scheme.

### Explanation
`urllib.request.urlopen` by default can process not only `http://` and `https://` schemes, but also `ftp://` and `file://`. If an attacker can manipulate the URL being fetched, they could exploit the `file://` scheme to access local files on the executing machine, leading to local file disclosure (Path Traversal) or Server-Side Request Forgery (SSRF).

Although in this specific script the URLs appear to be constructed using the `wikipedia.org` domain, relying solely on unvalidated input inside `urlopen` remains a poor security practice. It is crucial to strictly validate URL schemas to prevent potential manipulation if the context or inputs change in the future.

## Recommendations

### Code Changes

It is recommended to explicitly validate the URL scheme before calling `urllib.request.urlopen`. Ensure that the URL begins with `http://` or `https://`. After validating, append the `# nosec B310` comment to the `urlopen` line to safely suppress the Bandit warning.

**Example implementation:**

```python
if not url.startswith(('http://', 'https://')):
    raise ValueError("Invalid URL scheme. Only HTTP and HTTPS are permitted.")

req = urllib.request.Request(url, headers={'User-Agent': 'SigridKnowledgeBuilder/1.0'})
with urllib.request.urlopen(req) as response:  # nosec B310
    data = json.loads(response.read().decode())
```

Applying this structure to both lines 27 and 62 will resolve the vulnerabilities while satisfying the Bandit security check.
